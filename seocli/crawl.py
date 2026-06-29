#!/usr/bin/env python3
"""Crawl a website and extract SEO data with optional JavaScript rendering."""
import time
import requests
import socket
import ssl
import threading
import asyncio
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

from seocli.core.rate import RateLimiter
from seocli.core.link import LinkManager
from seocli.core.seo import SEOExtractor
from seocli.core.sitemap import SitemapParser
from seocli.core.issues import IssueDetector


def classify_fetch_error(exc_or_msg):
    """Classify a fetch error into dns/timeout/refused/ssl/connection types."""
    if isinstance(exc_or_msg, BaseException):
        seen = set()
        cur = exc_or_msg
        while cur is not None and id(cur) not in seen:
            seen.add(id(cur))
            if isinstance(cur, socket.gaierror):
                return 'dns_not_found'
            if isinstance(cur, ssl.SSLError) or isinstance(cur, requests.exceptions.SSLError):
                return 'ssl_error'
            if isinstance(cur, ConnectionRefusedError):
                return 'connection_refused'
            if isinstance(cur, (socket.timeout, requests.exceptions.Timeout)):
                return 'timeout'
            cur = getattr(cur, '__cause__', None) or getattr(cur, '__context__', None)
    msg = str(exc_or_msg).lower()
    dns = ('getaddrinfo failed', 'name or service not known', 'name resolution',
           'nodename nor servname', 'no address associated', 'name does not resolve',
           'temporary failure in name resolution', 'name_not_resolved',
           'err_name_not_resolved', 'nxdomain')
    if any(m in msg for m in dns):
        return 'dns_not_found'
    if 'timed out' in msg or 'timeout' in msg:
        return 'timeout'
    if 'refused' in msg or 'err_connection_refused' in msg:
        return 'connection_refused'
    if 'ssl' in msg or 'certificate' in msg or 'err_cert' in msg or 'tls' in msg:
        return 'ssl_error'
    return 'connection_error'


class Crawler:
    """Website crawler with SEO analysis. Crawls pages, extracts SEO data, detects issues."""

    def __init__(self, config=None):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'seocli/1.0 (SEO Crawler)'})
        self.base_url = None
        self.base_domain = None
        self.rate_limiter = None
        self.link_manager = None
        self.sitemap_parser = None
        self.issue_detector = None
        self.seo_extractor = SEOExtractor()
        self.js_renderer = None
        self.crawl_results = []
        self.results_lock = threading.Lock()
        self.is_running = False
        self.is_paused = False
        defaults = self._default_config()
        defaults.update(config or {})
        self.config = defaults
        self.stats = {'discovered': 0, 'crawled': 0, 'depth': 0, 'speed': 0.0, 'start_time': None}
        self.crawl_thread = None
        self._robots_cache = {}
        self._image_status_cache = {}
        nest_asyncio_applied = False
        try:
            import nest_asyncio
            nest_asyncio.apply()
            nest_asyncio_applied = True
        except ImportError:
            pass

    def _default_config(self):
        return {
            'max_depth': 3, 'max_urls': 500, 'delay': 0,
            'follow_redirects': True, 'crawl_external': False,
            'user_agent': 'seocli/1.0 (SEO Crawler)',
            'timeout': 10, 'retries': 1, 'respect_robots': True,
            'discover_sitemaps': True,
            'include_extensions': ['html', 'htm', 'php', 'asp', 'aspx', 'jsp'],
            'exclude_extensions': ['pdf', 'doc', 'docx', 'zip', 'exe', 'dmg'],
            'include_patterns': [], 'exclude_patterns': [],
            'concurrency': 5, 'enable_javascript': False,
            'js_wait_time': 3, 'js_timeout': 30, 'js_browser': 'chromium',
            'js_headless': True, 'js_max_concurrent_pages': 3,
            'enable_duplication_check': True, 'duplication_threshold': 0.85,
        }

    def crawl(self, url):
        """Start crawling from the given URL. Returns (success, message)."""
        if self.is_running:
            return False, "Crawl already in progress"

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parsed = urlparse(url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.base_domain = parsed.netloc

        # Initialize components
        if self.config['delay'] > 0:
            rps = 1.0 / self.config['delay']
        else:
            rps = 100.0
        self.rate_limiter = RateLimiter(rps)
        self.link_manager = LinkManager(self.base_domain)
        self.sitemap_parser = SitemapParser(self.session, self.base_domain, self.config['timeout'])
        self.issue_detector = IssueDetector()

        self.crawl_results.clear()
        self.stats = {'discovered': 0, 'crawled': 0, 'depth': 0, 'speed': 0.0, 'start_time': time.time()}

        # Add initial URL
        self.link_manager.add_url(url, 0)
        self.stats['discovered'] = 1

        # Discover sitemaps
        if self.config.get('discover_sitemaps', True):
            sitemap_urls = self.sitemap_parser.discover_sitemaps(url)
            for su in sitemap_urls:
                if self._should_crawl_url(su):
                    self.link_manager.add_url(su, 0)
            self.stats['discovered'] = self.link_manager.get_stats()['discovered']

        # Initialize JS renderer if needed
        if self.config.get('enable_javascript', False):
            from seocli.core.js import JavaScriptRenderer
            self.js_renderer = JavaScriptRenderer(self.config)

        self.is_running = True
        self.crawl_thread = threading.Thread(target=self._crawl_worker)
        self.crawl_thread.start()
        return True, "Crawl started"

    def wait(self):
        """Wait for the crawl to finish."""
        if self.crawl_thread and self.crawl_thread.is_alive():
            self.crawl_thread.join(timeout=300)

    def stop(self):
        """Stop the current crawl."""
        self.is_running = False
        if self.crawl_thread and self.crawl_thread.is_alive():
            self.crawl_thread.join(timeout=5)
        if self.js_renderer:
            try:
                asyncio.run(self.js_renderer.cleanup())
            except Exception:
                pass
            self.js_renderer = None

    def get_results(self):
        """Get all crawl results, links, issues, and stats."""
        if self.link_manager:
            self.link_manager.update_link_statuses(self.crawl_results)

        # Mark all linked_from
        for r in self.crawl_results:
            r['linked_from'] = self.link_manager.get_source_pages(r['url']) if self.link_manager else []

        return {
            'url': self.base_url or '',
            'stats': {
                'crawled': self.stats['crawled'],
                'discovered': self.link_manager.get_stats()['discovered'] if self.link_manager else 0,
                'depth': self.stats['depth'],
                'speed': round(self.stats['crawled'] / max(time.time() - (self.stats['start_time'] or time.time()), 1), 2),
                'elapsed_seconds': round(time.time() - (self.stats['start_time'] or time.time()), 1),
            },
            'pages': self.crawl_results.copy(),
            'links': self.link_manager.all_links.copy() if self.link_manager else [],
            'issues': self.issue_detector.get_issues() if self.issue_detector else [],
        }

    def _crawl_worker(self):
        """Main crawling worker."""
        if self.config.get('enable_javascript', False) and self.js_renderer:
            try:
                asyncio.run(self._crawl_async_with_js())
            finally:
                if self.js_renderer:
                    try:
                        asyncio.run(self.js_renderer.cleanup())
                    except Exception:
                        pass
                    self.js_renderer = None
        else:
            self._crawl_sync()

    def _crawl_sync(self):
        max_workers = self.config.get('concurrency', 5)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            active = {}
            while self.is_running:
                if self.is_paused:
                    time.sleep(1)
                    continue
                while len(active) < max_workers and self.stats['crawled'] < self.config['max_urls']:
                    url_info = self.link_manager.get_next_url() if self.link_manager else None
                    if not url_info:
                        break
                    current_url, depth = url_info
                    if depth > self.config['max_depth']:
                        continue
                    if self.config['delay'] > 0 and self.rate_limiter:
                        self.rate_limiter.acquire()
                    future = executor.submit(self._crawl_url, current_url, depth)
                    active[future] = current_url

                done = []
                for future in list(active.keys()):
                    if future.done():
                        done.append(future)
                        try:
                            result = future.result()
                            if result:
                                with self.results_lock:
                                    self.crawl_results.append(result)
                                    self.stats['crawled'] += 1
                                    self.stats['depth'] = max(self.stats['depth'], result.get('depth', 0))
                                if self.issue_detector:
                                    self.issue_detector.detect_issues(result)
                        except Exception:
                            pass
                for future in done:
                    del active[future]

                if self.stats['crawled'] >= self.config['max_urls']:
                    break
                link_stats = self.link_manager.get_stats() if self.link_manager else {'pending': 0}
                if link_stats['pending'] == 0 and len(active) == 0:
                    break
                time.sleep(0.001)

        # Duplication check
        if self.config.get('enable_duplication_check', True) and self.issue_detector and len(self.crawl_results) > 1:
            self.issue_detector.detect_duplication_issues(self.crawl_results, self.config.get('duplication_threshold', 0.85))

        self.is_running = False

    async def _crawl_async_with_js(self):
        await self.js_renderer.initialize()
        max_workers = self.config.get('js_max_concurrent_pages', 3)
        active = set()
        while self.is_running and self.stats['crawled'] < self.config['max_urls']:
            if self.is_paused:
                await asyncio.sleep(1)
                continue
            while len(active) < max_workers:
                url_info = self.link_manager.get_next_url() if self.link_manager else None
                if not url_info:
                    break
                current_url, depth = url_info
                if depth > self.config['max_depth']:
                    continue
                if self.config['delay'] > 0 and self.rate_limiter:
                    self.rate_limiter.acquire()
                task = asyncio.create_task(self._crawl_url_with_js(current_url, depth))
                active.add(task)
            if active:
                done, active = await asyncio.wait(active, timeout=0.01, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    try:
                        result = await task
                        if result:
                            with self.results_lock:
                                self.crawl_results.append(result)
                                self.stats['crawled'] += 1
                                self.stats['depth'] = max(self.stats['depth'], result.get('depth', 0))
                            if self.issue_detector:
                                self.issue_detector.detect_issues(result)
                    except Exception:
                        pass
            link_stats = self.link_manager.get_stats() if self.link_manager else {'pending': 0}
            if link_stats['pending'] == 0 and len(active) == 0:
                break
            await asyncio.sleep(0.001)
        if self.config.get('enable_duplication_check', True) and self.issue_detector and len(self.crawl_results) > 1:
            self.issue_detector.detect_duplication_issues(self.crawl_results, self.config.get('duplication_threshold', 0.85))
        self.is_running = False

    def _crawl_url(self, url, depth):
        """Crawl a single URL with requests + BeautifulSoup."""
        retries = self.config.get('retries', 1)
        start_time = time.time()
        try:
            response = None
            for attempt in range(retries + 1):
                try:
                    response = self.session.get(url, timeout=self.config['timeout'], allow_redirects=self.config['follow_redirects'])
                    break
                except Exception as e:
                    if attempt >= retries:
                        raise e
                    time.sleep(1)

            is_internal = self.link_manager.is_internal(url) if self.link_manager else True
            result = self.seo_extractor.create_empty_result(url, depth, response.status_code, None)

            result.update({
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', '').split(';')[0],
                'size': len(response.content),
                'is_internal': is_internal,
            })

            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                self.seo_extractor.extract_basic_seo_data(soup, result)
                self.seo_extractor.extract_meta_tags(soup, result)
                self.seo_extractor.extract_opengraph_tags(soup, result)
                self.seo_extractor.extract_twitter_tags(soup, result)
                self.seo_extractor.extract_canonical(soup, result)
                self.seo_extractor.extract_json_ld(soup, result)
                self.seo_extractor.extract_analytics_tracking(soup, response.text, result)
                self.seo_extractor.extract_images(soup, url, result)
                self.seo_extractor.extract_link_counts(soup, result, self.base_domain)
                self.seo_extractor.extract_hreflang(soup, result)
                self.seo_extractor.extract_schema_org(soup, result)

                if self.link_manager:
                    # Collect all links for reporting
                    self.link_manager.collect_all_links(soup, url, self.crawl_results)

                    # Check broken images
                    image_links = [l for l in self.link_manager.all_links
                                   if l.get('placement') == 'image' and l.get('target_status') is None]
                    if image_links:
                        self._check_image_statuses(image_links)
                        broken = [l for l in image_links
                                  if l.get('target_status') is not None and (l['target_status'] >= 400 or l['target_status'] == 0)]
                        if broken:
                            result['broken_images'] = [{'url': l['target_url'], 'status': l['target_status']} for l in broken]

                    # Extract links for further crawling
                    should_extract = is_internal and depth < self.config['max_depth']
                    if should_extract:
                        self.link_manager.extract_links(soup, url, depth + 1, self._should_crawl_url)

                result['linked_from'] = self.link_manager.get_source_pages(url) if self.link_manager else []
                with self.results_lock:
                    self.stats['discovered'] = self.link_manager.get_stats()['discovered'] if self.link_manager else 0

            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            return result

        except Exception as e:
            return self.seo_extractor.create_empty_result(url, depth, 0, str(e), error_type=classify_fetch_error(e))

    async def _crawl_url_with_js(self, url, depth):
        """Crawl a single URL with Playwright JS rendering."""
        start_time = time.time()
        try:
            html_content, status_code, error = await self.js_renderer.render_page(url)
            if error:
                return self.seo_extractor.create_empty_result(url, depth, status_code, error, error_type=classify_fetch_error(error) if status_code == 0 else None)

            is_internal = self.link_manager.is_internal(url) if self.link_manager else True
            result = self.seo_extractor.create_empty_result(url, depth, status_code, None)
            result.update({
                'status_code': status_code,
                'content_type': 'text/html',
                'size': len(html_content.encode('utf-8')),
                'is_internal': is_internal,
                'javascript_rendered': True,
            })

            soup = BeautifulSoup(html_content, 'html.parser')
            self.seo_extractor.extract_basic_seo_data(soup, result)
            self.seo_extractor.extract_meta_tags(soup, result)
            self.seo_extractor.extract_opengraph_tags(soup, result)
            self.seo_extractor.extract_twitter_tags(soup, result)
            self.seo_extractor.extract_canonical(soup, result)
            self.seo_extractor.extract_json_ld(soup, result)
            self.seo_extractor.extract_analytics_tracking(soup, html_content, result)
            self.seo_extractor.extract_images(soup, url, result)
            self.seo_extractor.extract_link_counts(soup, result, self.base_domain)
            self.seo_extractor.extract_hreflang(soup, result)
            self.seo_extractor.extract_schema_org(soup, result)

            if self.link_manager:
                self.link_manager.collect_all_links(soup, url, self.crawl_results)
                image_links = [l for l in self.link_manager.all_links if l.get('placement') == 'image' and l.get('target_status') is None]
                if image_links:
                    self._check_image_statuses(image_links)
                    broken = [l for l in image_links if l.get('target_status') is not None and (l['target_status'] >= 400 or l['target_status'] == 0)]
                    if broken:
                        result['broken_images'] = [{'url': l['target_url'], 'status': l['target_status']} for l in broken]
                if is_internal and depth < self.config['max_depth']:
                    self.link_manager.extract_links(soup, url, depth + 1, self._should_crawl_url)

            result['linked_from'] = self.link_manager.get_source_pages(url) if self.link_manager else []
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            return result

        except Exception as e:
            return self.seo_extractor.create_empty_result(url, depth, 0, f'JS rendering error: {str(e)}', error_type=classify_fetch_error(e))

    def _check_image_statuses(self, image_links):
        """HEAD-check image URLs to detect broken images. Uses per-crawl cache."""
        to_check = []
        for link in image_links:
            url = link['target_url']
            cached = self._image_status_cache.get(url)
            if cached is not None:
                link['target_status'] = cached
            elif link.get('target_status') is None:
                to_check.append(link)
        if not to_check:
            return

        def _head_check(link):
            url = link['target_url']
            try:
                resp = self.session.head(url, timeout=5, allow_redirects=True)
                link['target_status'] = resp.status_code
            except Exception:
                link['target_status'] = 0
            self._image_status_cache[url] = link['target_status']

        batch = to_check[:50]
        with ThreadPoolExecutor(max_workers=min(5, len(batch))) as pool:
            pool.map(_head_check, batch)

    def _should_crawl_url(self, url):
        """Check if URL should be crawled based on settings."""
        parsed = urlparse(url)
        if not self.config['crawl_external'] and self.link_manager and not self.link_manager.is_internal(url):
            return False
        if self.config['respect_robots'] and not self._check_robots_txt(url):
            return False
        path = parsed.path.lower()
        if '.' in path:
            ext = path.split('.')[-1]
            if ext in self.config['exclude_extensions']:
                return False
            if self.config['include_extensions'] and ext not in self.config['include_extensions']:
                return False
        if self.config['exclude_patterns']:
            import re
            for pattern in self.config['exclude_patterns']:
                if pattern and re.search(pattern, url):
                    return False
        if self.config['include_patterns']:
            import re
            if not any(pattern and re.search(pattern, url) for pattern in self.config['include_patterns']):
                return False
        return True

    def _check_robots_txt(self, url):
        """Check if URL is allowed by robots.txt"""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            if robots_url not in self._robots_cache:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                try:
                    response = self.session.get(robots_url, timeout=10)
                    if response.status_code in (401, 403):
                        rp.disallow_all = True
                    elif response.status_code >= 400:
                        rp.allow_all = True
                    else:
                        rp.parse(response.text.splitlines())
                    self._robots_cache[robots_url] = rp
                except Exception:
                    return True
            rp = self._robots_cache[robots_url]
            return rp.can_fetch(self.config.get('user_agent', '*'), url)
        except Exception:
            return True
