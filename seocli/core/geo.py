"""GEO (Generative Engine Optimization) signal extraction for AI search readiness."""
import re
from urllib.parse import urlparse


class GEOExtractor:
    """Extracts GEO signals from HTML for AI search engine optimization."""

    @staticmethod
    def extract_geo_signals(soup, result, url):
        """Extract signals that matter for AI search engines."""
        geo = {
            'has_structured_data': False,
            'has_faq_schema': False,
            'has_howto_schema': False,
            'has_article_schema': False,
            'content_structure_score': 0,
            'has_conclusion_section': False,
            'has_source_citations': False,
            'reading_time_minutes': 0,
            'entity_mentions': [],
            'ai_crawler_blocked': False,
            'has_llms_txt': False,
            'has_clear_author': False,
            'has_publish_date': False,
        }

        # Check structured data for AI-relevant types
        json_ld = result.get('json_ld', [])
        schema_org = result.get('schema_org', [])
        all_schema = json_ld + schema_org

        for item in json_ld:
            if isinstance(item, dict):
                geo['has_structured_data'] = True
                item_type = item.get('@type', '')
                if 'FAQ' in item_type:
                    geo['has_faq_schema'] = True
                if 'HowTo' in item_type:
                    geo['has_howto_schema'] = True
                if 'Article' in item_type or 'BlogPosting' in item_type:
                    geo['has_article_schema'] = True

        # Content structure score: check heading hierarchy
        h1 = result.get('h1', '')
        h2s = result.get('h2', [])
        h3s = result.get('h3', [])
        word_count = result.get('word_count', 0)

        structure_score = 0
        if h1: structure_score += 1
        if len(h2s) >= 2: structure_score += 1
        if len(h2s) >= 4: structure_score += 1
        if len(h3s) >= 2: structure_score += 1
        if word_count > 500: structure_score += 1
        if word_count > 1000: structure_score += 1
        geo['content_structure_score'] = min(structure_score, 6)

        # Check for conclusion section
        all_text = soup.get_text().lower()
        conclusion_patterns = [
            r'\bconclusion\b', r'\bsummary\b', r'\bkey takeaways\b',
            r'\bfinal thoughts\b', r'\bwrapping up\b', r'\bin summary\b',
            r'\bthe bottom line\b', r'\btl;dr\b',
        ]
        for pattern in conclusion_patterns:
            if re.search(pattern, all_text):
                geo['has_conclusion_section'] = True
                break

        # Check for source citations (links to external authoritative sources)
        ext_links = result.get('external_links', 0)
        if isinstance(ext_links, list):
            ext_links = len(ext_links)
        # Check for citation patterns in text
        citation_patterns = [
            r'\[\d+\]',  # [1], [2] style
            r'according to', r'source:', r'sources:', r'references',
            r'cited by', r'as noted by', r'as reported by',
        ]
        has_citation_text = any(re.search(p, all_text, re.IGNORECASE) for p in citation_patterns)
        geo['has_source_citations'] = has_citation_text or ext_links >= 3

        # Reading time (avg 238 words/min)
        geo['reading_time_minutes'] = max(1, round(word_count / 238))

        # Entity mentions (check for named entities: organizations, people, products)
        entity_patterns = {
            'organization': r'\b(Google|Microsoft|Apple|Amazon|Meta|OpenAI|Anthropic)\b',
            'technology': r'\b(API|SDK|AI|ML|LLM|GPT|REST|GraphQL|Kubernetes|Docker)\b',
            'standard': r'\b(W3C|ISO|RFC|IEEE|GDPR|WCAG|ARIA)\b',
        }
        for category, pattern in entity_patterns.items():
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                geo['entity_mentions'].extend(list(set(matches)))

        # Check if common AI crawlers are blocked in robots meta
        robots = result.get('robots', '').lower()
        meta_tags = result.get('meta_tags', {})
        has_ai_block = False
        for bot in ['gptbot', 'chatgpt', 'claude', 'anthropic', 'perplexity', 'ccbot']:
            if bot in robots or bot in str(meta_tags).lower():
                has_ai_block = True
                break
        geo['ai_crawler_blocked'] = has_ai_block

        # Check for llms.txt (AI-readable site map)
        geo['has_llms_txt'] = False  # Set by crawler if /llms.txt exists

        # Check for clear author
        author = result.get('author', '')
        geo['has_clear_author'] = bool(author)

        # Check for publish date in meta
        meta_tags = result.get('meta_tags', {})
        has_date = any(
            k in meta_tags for k in ['article:published_time', 'date', 'pubdate', 'dc.date']
        )
        geo['has_publish_date'] = has_date

        result['geo_signals'] = geo
