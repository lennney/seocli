"""SEO data extraction from HTML content"""
import re
import json
from urllib.parse import urljoin


class SEOExtractor:
    """Extracts SEO-related data from HTML content"""

    @staticmethod
    def extract_basic_seo_data(soup, result):
        """Extract basic SEO data (title, headings, meta description, etc.)"""
        title_tag = soup.find('title')
        result['title'] = title_tag.get_text().strip() if title_tag else ''

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        result['meta_description'] = meta_desc.get('content', '').strip() if meta_desc else ''

        h1_tag = soup.find('h1')
        result['h1'] = h1_tag.get_text().strip() if h1_tag else ''

        h2_tags = soup.find_all('h2')
        result['h2'] = [h2.get_text().strip() for h2 in h2_tags[:10]]

        h3_tags = soup.find_all('h3')
        result['h3'] = [h3.get_text().strip() for h3 in h3_tags[:10]]

        text_content = soup.get_text()
        words = re.findall(r'\b\w+\b', text_content)
        result['word_count'] = len(words)

        html_tag = soup.find('html')
        result['lang'] = html_tag.get('lang', '') if html_tag else ''

        charset_meta = soup.find('meta', attrs={'charset': True})
        if charset_meta:
            result['charset'] = charset_meta.get('charset', '')
        else:
            content_type_meta = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
            if content_type_meta:
                content = content_type_meta.get('content', '')
                charset_match = re.search(r'charset=([^;]+)', content)
                result['charset'] = charset_match.group(1) if charset_match else ''

    @staticmethod
    def extract_meta_tags(soup, result):
        """Extract various meta tags"""
        meta_tags = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name', '') or tag.get('property', '') or tag.get('http-equiv', '')
            content = tag.get('content', '')
            if name and not name.startswith('og:') and not name.startswith('twitter:'):
                meta_tags[name.lower()] = content

        result['viewport'] = meta_tags.get('viewport', '')
        result['robots'] = meta_tags.get('robots', '')
        result['author'] = meta_tags.get('author', '')
        result['keywords'] = meta_tags.get('keywords', '')
        result['generator'] = meta_tags.get('generator', '')
        result['theme_color'] = meta_tags.get('theme-color', '')
        result['meta_tags'] = meta_tags

    @staticmethod
    def extract_opengraph_tags(soup, result):
        """Extract OpenGraph tags"""
        og_tags = {}
        for tag in soup.find_all('meta', property=re.compile(r'^og:', re.I)):
            prop = tag.get('property', '')
            content = tag.get('content', '')
            if prop and content:
                og_tags[prop] = content
        # Also check attrs named 'name' with og: prefix (some pages do this)
        for tag in soup.find_all('meta', attrs={'name': re.compile(r'^og:', re.I)}):
            name = tag.get('name', '')
            content = tag.get('content', '')
            if name and content and name not in og_tags:
                og_tags[name] = content
        result['og_tags'] = og_tags

    @staticmethod
    def extract_twitter_tags(soup, result):
        """Extract Twitter Card tags"""
        twitter_tags = {}
        for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:', re.I)}):
            name = tag.get('name', '')
            content = tag.get('content', '')
            if name and content:
                twitter_tags[name] = content
        result['twitter_tags'] = twitter_tags

    @staticmethod
    def extract_canonical(soup, result):
        """Extract canonical URL"""
        canonical = soup.find('link', rel='canonical')
        result['canonical_url'] = canonical.get('href', '') if canonical else ''

    @staticmethod
    def extract_json_ld(soup, result):
        """Extract JSON-LD structured data"""
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Normalize to array
                if isinstance(data, dict):
                    data = [data]
                json_ld_data.extend(data)
            except (json.JSONDecodeError, TypeError):
                pass
        result['json_ld'] = json_ld_data

    @staticmethod
    def extract_analytics_tracking(soup, html_text, result):
        """Detect analytics and tracking scripts"""
        analytics = {
            'google_analytics': False,
            'gtag': False,
            'ga4_id': '',
            'gtm_id': '',
            'facebook_pixel': False,
            'hotjar': False,
            'mixpanel': False
        }
        html_lower = html_text.lower()
        if 'gtag' in html_lower or 'googletagmanager' in html_lower:
            analytics['gtag'] = True
        if 'google-analytics' in html_lower:
            analytics['google_analytics'] = True
        if 'facebook pixel' in html_lower or 'fbq(' in html_text:
            analytics['facebook_pixel'] = True
        if 'hotjar' in html_lower:
            analytics['hotjar'] = True
        if 'mixpanel' in html_lower:
            analytics['mixpanel'] = True
        # Extract GA4 / GTM IDs
        ga4_match = re.search(r'G-[A-Z0-9]+', html_text)
        if ga4_match:
            analytics['ga4_id'] = ga4_match.group(0)
        gtm_match = re.search(r'GTM-[A-Z0-9]+', html_text)
        if gtm_match:
            analytics['gtm_id'] = gtm_match.group(0)
        result['analytics'] = analytics

    @staticmethod
    def extract_images(soup, base_url, result):
        """Extract image information"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not src:
                continue
            absolute_src = urljoin(base_url, src)
            images.append({
                'src': absolute_src,
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        result['images'] = images

    @staticmethod
    def extract_link_counts(soup, result, base_domain):
        """Count internal and external links"""
        internal = 0
        external = 0
        from urllib.parse import urlparse
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                continue
            absolute = urljoin(result['url'], href)
            parsed = urlparse(absolute)
            if parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain):
                internal += 1
            else:
                external += 1
        result['internal_links'] = internal
        result['external_links'] = external

    @staticmethod
    def extract_hreflang(soup, result):
        """Extract hreflang tags"""
        hreflangs = []
        for link in soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True}):
            hreflangs.append({
                'hreflang': link.get('hreflang', ''),
                'href': link.get('href', '')
            })
        result['hreflang'] = hreflangs

    @staticmethod
    def extract_schema_org(soup, result):
        """Extract Schema.org markup (non-JSON-LD)"""
        schemas = []
        for itemscope in soup.find_all(itemscope=True):
            itemtype = itemscope.get('itemtype', '')
            if itemtype:
                props = {}
                for prop in itemscope.find_all(itemprop=True):
                    name = prop.get('itemprop', '')
                    content = prop.get('content') or prop.get_text(strip=True)
                    if name:
                        props[name] = content
                schemas.append({
                    'type': itemtype,
                    'properties': props
                })
        result['schema_org'] = schemas

    @staticmethod
    def extract_form_presence(soup, result):
        """Detect if page contains a login/signup/checkout form."""
        forms = soup.find_all('form')
        for form in forms:
            action = (form.get('action', '') or '').lower()
            has_password = form.find('input', type='password') is not None
            if has_password or any(kw in action for kw in ['login', 'signin', 'signup', 'register', 'checkout', 'auth']):
                result['has_form'] = True
                return
        result['has_form'] = bool(forms)

    @staticmethod
    def extract_accessibility_data(soup, result):
        """Extract ARIA attributes, tabindex, skip links, contrast issues."""
        aria_roles = set()
        for el in soup.find_all(attrs={'role': True}):
            aria_roles.add(el.get('role', ''))

        positive_tabindex = []
        for el in soup.find_all(attrs={'tabindex': True}):
            try:
                if int(el.get('tabindex', '0')) > 0:
                    positive_tabindex.append(str(el.name))
            except ValueError:
                pass

        has_skip_link = False
        for link in soup.find_all('a', href=True):
            href = (link.get('href', '') or '').lower()
            text = (link.get_text() or '').lower()
            if href.startswith('#') and any(kw in text for kw in ['skip', 'jump to content', 'main content']):
                has_skip_link = True
                break

        potential_contrast_issues = 0
        for el in soup.find_all(style=True):
            style = (el.get('style', '') or '').lower()
            if 'color' in style and ('background' in style or 'bg' in style):
                potential_contrast_issues += 1

        result['accessibility'] = {
            'aria_roles': sorted(aria_roles),
            'aria_labels_count': len(soup.find_all(attrs={'aria-label': True})),
            'positive_tabindex_elements': positive_tabindex,
            'has_skip_link': has_skip_link,
            'potential_contrast_issues': potential_contrast_issues,
        }

    @staticmethod
    def extract_cwv_signals(soup, result):
        """Extract signals that correlate with Core Web Vitals issues (static analysis only)."""
        cwv = {
            'large_images_without_dimensions': 0,
            'dom_element_count': 0,
            'missing_font_display': False,
            'missing_preconnect': False,
            'inline_scripts_count': 0,
            'inline_styles_count': 0,
            'render_blocking_resources': 0,
        }

        cwv['dom_element_count'] = len(soup.find_all())

        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not img.get('width') and not img.get('height') and src:
                cwv['large_images_without_dimensions'] += 1

        for style in soup.find_all('style'):
            css = style.string or ''
            if '@font-face' in css and 'font-display' not in css:
                cwv['missing_font_display'] = True
                break

        has_preconnect = False
        for link in soup.find_all('link'):
            rel = link.get('rel', '')
            if isinstance(rel, list):
                rel = ' '.join(rel)
            if 'preconnect' in rel or 'dns-prefetch' in rel:
                has_preconnect = True
                break
        cwv['missing_preconnect'] = not has_preconnect

        cwv['inline_scripts_count'] = len([s for s in soup.find_all('script') if not s.get('src') and not s.get('defer') and not s.get('async')])
        cwv['inline_styles_count'] = len(soup.find_all('style'))
        cwv['render_blocking_resources'] = (
            len([s for s in soup.find_all('script', src=True) if not s.get('defer') and not s.get('async')])
            + len(soup.find_all('link', rel='stylesheet'))
        )

        result['cwv_signals'] = cwv

    @staticmethod
    def create_empty_result(url, depth, status_code, error, error_type=None):
        """Create a result for failed requests"""
        return {
            'url': url,
            'status_code': status_code,
            'error_type': error_type,
            'error': error,
            'content_type': '',
            'size': 0,
            'is_internal': True,
            'depth': depth,
            'title': '',
            'meta_description': '',
            'h1': '', 'h2': [], 'h3': [],
            'word_count': 0,
            'meta_tags': {}, 'og_tags': {}, 'twitter_tags': {},
            'canonical_url': '', 'lang': '', 'charset': '',
            'viewport': '', 'robots': '', 'author': '', 'keywords': '',
            'generator': '', 'theme_color': '',
            'json_ld': [],
            'analytics': {}, 'images': [],
            'internal_links': 0, 'external_links': 0,
            'response_time': 0,
            'redirects': [], 'hreflang': [], 'schema_org': [],
            'linked_from': [],
            'response_headers': {},
            'has_form': False,
            'accessibility': {
                'aria_roles': [],
                'aria_labels_count': 0,
                'positive_tabindex_elements': [],
                'has_skip_link': False,
                'potential_contrast_issues': 0,
            },
            'cwv_signals': {
                'large_images_without_dimensions': 0,
                'dom_element_count': 0,
                'missing_font_display': False,
                'missing_preconnect': False,
                'inline_scripts_count': 0,
                'inline_styles_count': 0,
                'render_blocking_resources': 0,
            },
        }
