"""SEO issue detection and reporting"""
import threading
from fnmatch import fnmatch
from urllib.parse import urlparse
from difflib import SequenceMatcher


class IssueDetector:
    """Detects SEO and technical issues in crawled pages"""

    def __init__(self, exclusion_patterns=None):
        self.exclusion_patterns = exclusion_patterns or []
        self.detected_issues = []
        self.issues_lock = threading.Lock()

    def detect_issues(self, result):
        """Detect SEO issues for a crawled URL"""
        url = result.get('url', '')
        if self._should_exclude(url):
            return
        issues = []
        self._check_title_issues(result, issues)
        self._check_meta_description_issues(result, issues)
        self._check_heading_issues(result, issues)
        self._check_content_issues(result, issues)
        self._check_status_issues(result, issues)
        self._check_mobile_issues(result, issues)
        self._check_accessibility_issues(result, issues)
        self._check_social_media_issues(result, issues)
        self._check_structured_data_issues(result, issues)
        self._check_performance_issues(result, issues)
        self._check_indexability_issues(result, issues)
        self._check_broken_image_issues(result, issues)
        with self.issues_lock:
            self.detected_issues.extend(issues)

    def _check_title_issues(self, result, issues):
        url, title = result.get('url', ''), result.get('title', '')
        if not title:
            issues.append({'url': url, 'type': 'error', 'category': 'SEO', 'issue': 'Missing Title Tag', 'details': 'Page has no title tag'})
        elif len(title) > 60:
            issues.append({'url': url, 'type': 'warning', 'category': 'SEO', 'issue': 'Title Too Long', 'details': f'Title is {len(title)} characters (recommended: ≤60)'})
        elif len(title) < 30:
            issues.append({'url': url, 'type': 'warning', 'category': 'SEO', 'issue': 'Title Too Short', 'details': f'Title is {len(title)} characters (recommended: 30-60)'})

    def _check_meta_description_issues(self, result, issues):
        url, desc = result.get('url', ''), result.get('meta_description', '')
        if not desc:
            issues.append({'url': url, 'type': 'error', 'category': 'SEO', 'issue': 'Missing Meta Description', 'details': 'Page has no meta description'})
        elif len(desc) > 160:
            issues.append({'url': url, 'type': 'warning', 'category': 'SEO', 'issue': 'Meta Description Too Long', 'details': f'Description is {len(desc)} characters (recommended: ≤160)'})
        elif len(desc) < 120:
            issues.append({'url': url, 'type': 'warning', 'category': 'SEO', 'issue': 'Meta Description Too Short', 'details': f'Description is {len(desc)} characters (recommended: 120-160)'})

    def _check_heading_issues(self, result, issues):
        url = result.get('url', '')
        if not result.get('h1'):
            issues.append({'url': url, 'type': 'error', 'category': 'SEO', 'issue': 'Missing H1 Tag', 'details': 'Page has no H1 heading'})

    def _check_content_issues(self, result, issues):
        url = result.get('url', '')
        wc = result.get('word_count', 0)
        if wc < 300:
            issues.append({'url': url, 'type': 'warning', 'category': 'Content', 'issue': 'Thin Content', 'details': f'Page has only {wc} words (recommended: ≥300)'})

    def _check_status_issues(self, result, issues):
        url, status = result.get('url', ''), result.get('status_code', 0)
        if status == 0:
            et = result.get('error_type')
            labels = {
                'dns_not_found': ('DNS Not Found', 'Domain does not resolve.'),
                'connection_refused': ('Connection Refused', 'Server actively refused the connection.'),
                'timeout': ('Request Timeout', 'Server did not respond in time.'),
                'ssl_error': ('SSL/TLS Error', 'Could not establish a secure connection.'),
                'connection_error': ('Connection Error', 'Could not connect to the server.'),
            }
            if et and et in labels:
                issues.append({'url': url, 'type': 'error', 'category': 'Technical', 'issue': labels[et][0], 'details': labels[et][1]})
        elif 400 <= status < 500:
            issues.append({'url': url, 'type': 'error', 'category': 'Technical', 'issue': f'{status} Client Error', 'details': f'URL returned HTTP {status}'})
        elif 500 <= status < 600:
            issues.append({'url': url, 'type': 'error', 'category': 'Technical', 'issue': f'{status} Server Error', 'details': f'URL returned HTTP {status}'})
        elif 300 <= status < 400:
            issues.append({'url': url, 'type': 'info', 'category': 'Technical', 'issue': f'{status} Redirect', 'details': 'URL redirects to another location'})
        # Canonical checks
        canon = result.get('canonical_url', '')
        if not canon:
            issues.append({'url': url, 'type': 'warning', 'category': 'Technical', 'issue': 'Missing Canonical URL', 'details': 'Page has no canonical URL specified'})
        elif canon != url:
            issues.append({'url': url, 'type': 'warning', 'category': 'Technical', 'issue': 'Canonical URL Different', 'details': f'Canonical points to: {canon}'})

    def _check_mobile_issues(self, result, issues):
        if not result.get('viewport'):
            issues.append({'url': result.get('url', ''), 'type': 'error', 'category': 'Mobile', 'issue': 'Missing Viewport Meta Tag', 'details': 'Page is not mobile-optimized'})

    def _check_accessibility_issues(self, result, issues):
        url = result.get('url', '')
        if not result.get('lang'):
            issues.append({'url': url, 'type': 'warning', 'category': 'Accessibility', 'issue': 'Missing Language Attribute', 'details': 'HTML tag has no lang attribute'})
        images = result.get('images', [])
        no_alt = [img for img in images if not img.get('alt')]
        if no_alt:
            issues.append({'url': url, 'type': 'warning', 'category': 'Accessibility', 'issue': 'Images Without Alt Text', 'details': f'{len(no_alt)} of {len(images)} images lack alt text'})

    def _check_social_media_issues(self, result, issues):
        url = result.get('url', '')
        if not result.get('og_tags'):
            issues.append({'url': url, 'type': 'warning', 'category': 'Social', 'issue': 'Missing OpenGraph Tags', 'details': 'Page has no OpenGraph tags for social sharing'})
        if not result.get('twitter_tags'):
            issues.append({'url': url, 'type': 'warning', 'category': 'Social', 'issue': 'Missing Twitter Card Tags', 'details': 'Page has no Twitter Card tags'})

    def _check_structured_data_issues(self, result, issues):
        if not result.get('json_ld') and not result.get('schema_org'):
            issues.append({'url': result.get('url', ''), 'type': 'error', 'category': 'Structured Data', 'issue': 'No Structured Data', 'details': 'Page has no JSON-LD or Schema.org markup'})

    def _check_performance_issues(self, result, issues):
        url, rt, size = result.get('url', ''), result.get('response_time', 0), result.get('size', 0)
        if rt > 3000:
            issues.append({'url': url, 'type': 'error', 'category': 'Performance', 'issue': 'Slow Response Time', 'details': f'Page took {rt}ms (recommended: <3000ms)'})
        elif rt > 1000:
            issues.append({'url': url, 'type': 'warning', 'category': 'Performance', 'issue': 'Moderate Response Time', 'details': f'Page took {rt}ms (recommended: <1000ms)'})
        if size > 3 * 1024 * 1024:
            issues.append({'url': url, 'type': 'error', 'category': 'Performance', 'issue': 'Large Page Size', 'details': f'Page size is {size/1024/1024:.1f}MB (recommended: <3MB)'})
        elif size > 1 * 1024 * 1024:
            issues.append({'url': url, 'type': 'warning', 'category': 'Performance', 'issue': 'Moderate Page Size', 'details': f'Page size is {size/1024/1024:.1f}MB (recommended: <1MB)'})

    def _check_indexability_issues(self, result, issues):
        url, robots = result.get('url', ''), result.get('robots', '').lower()
        if 'noindex' in robots:
            issues.append({'url': url, 'type': 'error', 'category': 'Indexability', 'issue': 'Noindex Tag Present', 'details': 'Page has noindex directive — blocked from search engines'})
        if 'nofollow' in robots:
            issues.append({'url': url, 'type': 'error', 'category': 'Indexability', 'issue': 'Nofollow Tag Present', 'details': 'Links on this page have nofollow directive'})

    def _check_broken_image_issues(self, result, issues):
        url = result.get('url', '')
        for img in result.get('broken_images', []):
            status = img.get('status', 0)
            img_url = img.get('url', '')
            if status == 0:
                issues.append({'url': url, 'type': 'error', 'category': 'Content', 'issue': 'Broken Image (No Response)', 'details': f'Image does not respond: {img_url}'})
            elif status >= 400:
                issues.append({'url': url, 'type': 'error', 'category': 'Content', 'issue': f'Broken Image ({status})', 'details': f'Image returned {status}: {img_url}'})

    def detect_duplication_issues(self, all_results, similarity_threshold=0.85):
        """Detect content duplication across all crawled pages (O(n²), use on small sets)."""
        issues = []
        processed_pairs = set()
        for i, r1 in enumerate(all_results):
            url1 = r1.get('url', '')
            if self._should_exclude(url1):
                continue
            for j, r2 in enumerate(all_results):
                if i >= j:
                    continue
                url2 = r2.get('url', '')
                if self._should_exclude(url2):
                    continue
                pair = tuple(sorted([url1, url2]))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                sim = self._calculate_content_similarity(r1, r2)
                if sim >= similarity_threshold:
                    issues.append({'url': url1, 'type': 'warning', 'category': 'Duplication', 'issue': 'Duplicate Content Detected', 'details': f'Content is {sim*100:.1f}% similar to {url2}'})
                    issues.append({'url': url2, 'type': 'warning', 'category': 'Duplication', 'issue': 'Duplicate Content Detected', 'details': f'Content is {sim*100:.1f}% similar to {url1}'})
        with self.issues_lock:
            self.detected_issues.extend(issues)

    def _calculate_content_similarity(self, r1, r2):
        """Calculate similarity ratio between two page results."""
        t1, t2 = r1.get('title', '').lower().strip(), r2.get('title', '').lower().strip()
        d1, d2 = r1.get('meta_description', '').lower().strip(), r2.get('meta_description', '').lower().strip()
        h1_1, h1_2 = r1.get('h1', '').lower().strip(), r2.get('h1', '').lower().strip()
        w1, w2 = r1.get('word_count', 0), r2.get('word_count', 0)
        t_sim = SequenceMatcher(None, t1, t2).ratio() if t1 and t2 else 0
        d_sim = SequenceMatcher(None, d1, d2).ratio() if d1 and d2 else 0
        h_sim = SequenceMatcher(None, h1_1, h1_2).ratio() if h1_1 and h1_2 else 0
        w_sim = min(w1, w2) / max(w1, w2) if w1 and w2 else 0
        return t_sim * 0.35 + d_sim * 0.35 + h_sim * 0.20 + w_sim * 0.10

    def _should_exclude(self, url):
        """Check if URL matches exclusion patterns"""
        path = urlparse(url).path
        for pattern in self.exclusion_patterns:
            if '*' in pattern:
                if fnmatch(path, pattern):
                    return True
            elif path == pattern or path.startswith(pattern.rstrip('*')):
                return True
        return False

    def get_issues(self):
        """Get all detected issues"""
        with self.issues_lock:
            return self.detected_issues.copy()

    def reset(self):
        """Reset detected issues"""
        with self.issues_lock:
            self.detected_issues.clear()
