"""Shared pytest fixtures for seocli tests."""

from __future__ import annotations

from typing import Any

import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def basic_html() -> str:
    """Return a well-formed HTML page with comprehensive SEO elements."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page Title for Basic SEO Test Fixture V2</title>
    <meta name="description" content="This is a comprehensive test page designed for SEO auditing purposes. It includes various meta tags, structured data, and content elements to validate crawler functionality.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://example.com/page">
    <meta property="og:title" content="OG Test Title">
    <meta property="og:description" content="Open Graph description for testing purposes.">
    <meta property="og:image" content="https://example.com/image.jpg">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Twitter Test Title">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Example Site",
        "url": "https://example.com"
    }
    </script>
</head>
<body>
    <h1>Main Heading</h1>
    <h2>Section One</h2>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    <h2>Section Two</h2>
    <p>Additional paragraph content for testing purposes. This page contains multiple sections to verify heading extraction and content analysis features of the SEO crawler.</p>
    <a href="https://example.com/about">Internal Link</a>
    <a href="https://external-site.com">External Link</a>
    <img src="https://example.com/photo.jpg" alt="Descriptive photo alt text">
    <img src="https://example.com/banner.png" alt="">
</body>
</html>"""


@pytest.fixture
def basic_soup(basic_html: str) -> BeautifulSoup:
    """Return BeautifulSoup object parsed from basic_html."""
    return BeautifulSoup(basic_html, "html.parser")


@pytest.fixture
def empty_html() -> str:
    """Return a bare-minimum HTML page with almost no SEO elements."""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <p>A tiny paragraph.</p>
</body>
</html>"""


@pytest.fixture
def empty_soup(empty_html: str) -> BeautifulSoup:
    """Return BeautifulSoup object parsed from empty_html."""
    return BeautifulSoup(empty_html, "html.parser")


@pytest.fixture
def basic_page_result() -> dict[str, Any]:
    """Return a dict that mirrors a full seocli crawl result for basic_html."""
    return {
        "url": "https://example.com/page",
        "status_code": 200,
        "title": "Test Page Title for Basic SEO Test Fixture V2",
        "meta_description": "This is a comprehensive test page designed for SEO auditing purposes. It includes various meta tags, structured data, and content elements to validate crawler functionality.",
        "h1": "Main Heading",
        "h2": ["Section One", "Section Two"],
        "h3": [],
        "word_count": 150,
        "lang": "en",
        "charset": "UTF-8",
        "viewport": "width=device-width, initial-scale=1.0",
        "robots": "index, follow",
        "canonical_url": "https://example.com/page",
        "og_tags": {
            "og:title": "OG Test Title",
            "og:description": "Open Graph description for testing purposes.",
            "og:image": "https://example.com/image.jpg",
        },
        "twitter_tags": {
            "twitter:card": "summary_large_image",
            "twitter:title": "Twitter Test Title",
        },
        "json_ld": [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Example Site",
                "url": "https://example.com",
            }
        ],
        "images": [
            {"src": "https://example.com/photo.jpg", "alt": "Descriptive photo alt text"},
            {"src": "https://example.com/banner.png", "alt": ""},
        ],
        "internal_links": [
            {"href": "https://example.com/about", "text": "Internal Link"},
        ],
        "external_links": [
            {"href": "https://external-site.com", "text": "External Link"},
        ],
        "response_time": 234.5,
        "hreflang": [],
        "schema_org": [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Example Site",
                "url": "https://example.com",
            }
        ],
        "analytics": {},
        "meta_tags": {
            "charset": "UTF-8",
            "viewport": "width=device-width, initial-scale=1.0",
            "description": "This is a comprehensive test page designed for SEO auditing purposes. It includes various meta tags, structured data, and content elements to validate crawler functionality.",
            "robots": "index, follow",
        },
        "redirects": [],
        "broken_images": [],
        "linked_from": [],
        "response_headers": {
            "content-type": "text/html; charset=UTF-8",
            "server": "test",
        },
        "has_form": False,
        "accessibility": {},
        "cwv_signals": {},
        "geo_signals": {
            "has_structured_data": True,
            "has_faq_schema": False,
            "has_howto_schema": False,
            "has_article_schema": False,
            "content_structure_score": 4,
            "has_conclusion_section": True,
            "has_source_citations": True,
            "reading_time_minutes": 1,
            "entity_mentions": [],
            "ai_crawler_blocked": False,
            "has_llms_txt": False,
            "has_clear_author": False,
            "has_publish_date": False,
        },
        "error_type": None,
        "error": None,
        "content_type": "text/html; charset=UTF-8",
        "size": 1450,
        "is_internal": True,
        "depth": 0,
    }