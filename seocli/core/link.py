"""Link management and extraction"""
import threading
from urllib.parse import urljoin, urlparse
from collections import deque


class LinkManager:
    """Manages link discovery, tracking, and extraction"""

    def __init__(self, base_domain):
        self.base_domain = base_domain
        self.visited_urls = set()
        self.discovered_urls = deque()
        self.all_discovered_urls = set()
        self.all_links = []
        self.links_set = set()
        self.source_pages = {}  # Maps target_url -> list of source_urls
        self.urls_lock = threading.Lock()
        self.links_lock = threading.Lock()

    def extract_links(self, soup, current_url, depth, should_crawl_callback):
        """Extract links from HTML and add to discovery queue"""
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            absolute_url = urljoin(current_url, href)
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            with self.urls_lock:
                if clean_url not in self.source_pages:
                    self.source_pages[clean_url] = []
                if current_url not in self.source_pages[clean_url]:
                    self.source_pages[clean_url].append(current_url)
                if (clean_url not in self.visited_urls and
                    clean_url not in self.all_discovered_urls and
                    clean_url != current_url):
                    if should_crawl_callback(clean_url):
                        self.discovered_urls.append((clean_url, depth))
                        self.all_discovered_urls.add(clean_url)

    def get_next_url(self):
        """Get the next URL to crawl"""
        with self.urls_lock:
            if self.discovered_urls:
                next_url, depth = self.discovered_urls.popleft()
                self.visited_urls.add(next_url)
                return next_url, depth
            return None

    def collect_all_links(self, soup, source_url, existing_results):
        """Collect all links from a page for reporting"""
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'].strip()
            if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            absolute_url = urljoin(source_url, href)
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            is_internal = self.is_internal(clean_url)
            link_key = f"{source_url}|{clean_url}"
            with self.links_lock:
                if link_key not in self.links_set:
                    self.links_set.add(link_key)
                    self.all_links.append({
                        'source_url': source_url,
                        'target_url': clean_url,
                        'anchor_text': link.get_text().strip()[:100],
                        'is_internal': is_internal,
                        'target_domain': parsed.netloc,
                        'target_status': None,
                        'placement': 'body'
                    })

        # Also collect image links
        imgs = soup.find_all('img', src=True)
        for img in imgs:
            src = img['src'].strip()
            absolute_url = urljoin(source_url, src)
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            is_internal = self.is_internal(clean_url)
            link_key = f"{source_url}|{clean_url}"
            with self.links_lock:
                if link_key not in self.links_set:
                    self.links_set.add(link_key)
                    self.all_links.append({
                        'source_url': source_url,
                        'target_url': clean_url,
                        'anchor_text': img.get('alt', '')[:100],
                        'is_internal': is_internal,
                        'target_domain': parsed.netloc,
                        'target_status': None,
                        'placement': 'image'
                    })

    def get_source_pages(self, url):
        """Get list of pages that link to this URL"""
        return list(self.source_pages.get(url, []))

    def is_internal(self, url):
        """Check if URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.base_domain or parsed.netloc.endswith('.' + self.base_domain)

    def add_url(self, url, depth):
        """Manually add a URL to the discovery queue"""
        with self.urls_lock:
            if url not in self.all_discovered_urls and url not in self.visited_urls:
                self.discovered_urls.append((url, depth))
                self.all_discovered_urls.add(url)

    def get_stats(self):
        """Get link statistics"""
        with self.urls_lock:
            return {
                'discovered': len(self.all_discovered_urls),
                'visited': len(self.visited_urls),
                'pending': len(self.discovered_urls)
            }

    def update_link_statuses(self, crawl_results):
        """Update link target_status from crawled URL results"""
        status_lookup = {r['url']: r.get('status_code') for r in crawl_results if r.get('url')}
        for link in self.all_links:
            target = link.get('target_url')
            if target in status_lookup:
                link['target_status'] = status_lookup[target]

    def reset(self):
        """Reset all state"""
        with self.urls_lock:
            self.visited_urls.clear()
            self.discovered_urls.clear()
            self.all_discovered_urls.clear()
            self.all_links.clear()
            self.links_set.clear()
            self.source_pages.clear()
