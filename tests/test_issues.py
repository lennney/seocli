"""Tests for IssueDetector -- all existing rules."""
from __future__ import annotations

from typing import Any

import pytest

from seocli.core.issues import IssueDetector


@pytest.fixture
def detector() -> Any:
    d = IssueDetector()
    yield d
    d.reset()


class TestTitleIssues:
    """_check_title_issues: missing, too long, too short, and ok."""

    def test_missing_title(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["title"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Title Tag" for i in issues)

    def test_title_too_long(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["title"] = "A" * 61
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Title Too Long" for i in issues)

    def test_title_too_short(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["title"] = "Hi"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Title Too Short" for i in issues)

    def test_title_ok(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["title"] = "A" * 45
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        title_issues = {"Missing Title Tag", "Title Too Long", "Title Too Short"}
        assert not any(i["issue"] in title_issues for i in issues)


class TestMetaDescriptionIssues:
    """_check_meta_description_issues: missing, too long, too short."""

    def test_missing_description(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["meta_description"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Meta Description" for i in issues)

    def test_description_too_long(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["meta_description"] = "A" * 161
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Meta Description Too Long" for i in issues)

    def test_description_too_short(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["meta_description"] = "Short"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Meta Description Too Short" for i in issues)


class TestHeadingIssues:
    """_check_heading_issues: missing h1."""

    def test_missing_h1(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["h1"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing H1 Tag" for i in issues)


class TestContentIssues:
    """_check_content_issues: thin content."""

    def test_thin_content(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["word_count"] = 50
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Thin Content" for i in issues)

    def test_no_thin_content_flag_for_sufficient_words(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["word_count"] = 500
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any(i["issue"] == "Thin Content" for i in issues)


class TestStatusIssues:
    """_check_status_issues: 4xx, 5xx, 3xx, canonical, dns, ssl."""

    def test_404_error(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["status_code"] = 404
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any("404" in i["issue"] for i in issues)

    def test_500_error(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["status_code"] = 500
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any("500" in i["issue"] for i in issues)

    def test_301_redirect_info(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["status_code"] = 301
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any("Redirect" in i["issue"] for i in issues)

    def test_missing_canonical(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["canonical_url"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Canonical URL" for i in issues)

    def test_canonical_mismatch(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["canonical_url"] = "https://other.com/"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Canonical URL Different" for i in issues)

    def test_dns_not_found_error(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["status_code"] = 0
        basic_page_result["error_type"] = "dns_not_found"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "DNS Not Found" for i in issues)

    def test_ssl_error(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["status_code"] = 0
        basic_page_result["error_type"] = "ssl_error"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "SSL/TLS Error" for i in issues)


class TestMobileIssues:
    """_check_mobile_issues: missing viewport."""

    def test_missing_viewport(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["viewport"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Viewport Meta Tag" for i in issues)


class TestAccessibilityIssues:
    """_check_accessibility_issues: missing lang, images alt text."""

    def test_missing_lang(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["lang"] = ""
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Language Attribute" for i in issues)

    def test_images_without_alt(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        matches = [i for i in issues if i["issue"] == "Images Without Alt Text"]
        assert len(matches) == 1
        assert "1 of 2" in matches[0]["details"]


class TestAccessibilityAdvanced:
    def test_positive_tabindex(self, detector, basic_page_result):
        basic_page_result['accessibility'] = {
            'aria_roles': [],
            'aria_labels_count': 0,
            'positive_tabindex_elements': ['div'],
            'has_skip_link': False,
            'potential_contrast_issues': 0,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Positive Tabindex' in i['issue'] for i in issues)

    def test_missing_skip_link(self, detector, basic_page_result):
        basic_page_result['accessibility'] = {
            'aria_roles': [],
            'aria_labels_count': 0,
            'positive_tabindex_elements': [],
            'has_skip_link': False,
            'potential_contrast_issues': 0,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Skip Link' in i['issue'] for i in issues)

    def test_no_aria_roles(self, detector, basic_page_result):
        basic_page_result['accessibility'] = {
            'aria_roles': [],
            'aria_labels_count': 0,
            'positive_tabindex_elements': [],
            'has_skip_link': True,
            'potential_contrast_issues': 0,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('ARIA Landmarks' in i['issue'] for i in issues)

    def test_potential_contrast_issues(self, detector, basic_page_result):
        basic_page_result['accessibility'] = {
            'aria_roles': ['main'],
            'aria_labels_count': 2,
            'positive_tabindex_elements': [],
            'has_skip_link': True,
            'potential_contrast_issues': 3,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Contrast Issues' in i['issue'] for i in issues)


class TestSocialMediaIssues:
    """_check_social_media_issues: og and twitter tags."""

    def test_missing_og(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["og_tags"] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing OpenGraph Tags" for i in issues)

    def test_missing_twitter(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["twitter_tags"] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Twitter Card Tags" for i in issues)


class TestStructuredDataIssues:
    """_check_structured_data_issues: no structured data."""

    def test_no_structured_data(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["json_ld"] = []
        basic_page_result["schema_org"] = []
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "No Structured Data" for i in issues)

    def test_has_jsonld_no_warning(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any(i["issue"] == "No Structured Data" for i in issues)


class TestPerformanceIssues:
    """_check_performance_issues: slow/moderate/large/fast."""

    def test_slow_response(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["response_time"] = 3500
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Slow Response Time" for i in issues)

    def test_moderate_response(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["response_time"] = 1500
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Moderate Response Time" for i in issues)

    def test_large_page(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["size"] = 4 * 1024 * 1024
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Large Page Size" for i in issues)

    def test_fast_page_no_issue(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["response_time"] = 200
        basic_page_result["size"] = 50000
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any(i["category"] == "Performance" for i in issues)


class TestIndexabilityIssues:
    """_check_indexability_issues: noindex, nofollow."""

    def test_noindex(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["robots"] = "noindex, nofollow"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Noindex Tag Present" for i in issues)

    def test_nofollow(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["robots"] = "nofollow"
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Nofollow Tag Present" for i in issues)


class TestBrokenImageIssues:
    """_check_broken_image_issues: no response and 404."""

    def test_broken_image_no_response(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["broken_images"] = [{"url": "https://x.com/dead.jpg", "status": 0}]
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Broken Image (No Response)" for i in issues)

    def test_broken_image_404(self, detector: IssueDetector, basic_page_result: dict[str, Any]) -> None:
        basic_page_result["broken_images"] = [{"url": "https://x.com/dead.jpg", "status": 404}]
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Broken Image (404)" for i in issues)


class TestDuplicationIssues:
    """detect_duplication_issues: duplicate and unique content."""

    def test_duplicate_content_detected(self, detector: IssueDetector) -> None:
        identical = {"url": "https://example.com/a", "title": "Same Page", "meta_description": "Same description here for testing.", "h1": "Same Heading", "word_count": 300}
        also_identical = {"url": "https://example.com/b", "title": "Same Page", "meta_description": "Same description here for testing.", "h1": "Same Heading", "word_count": 300}
        detector.detect_duplication_issues([identical, also_identical])
        issues = detector.get_issues()
        assert any(i["issue"] == "Duplicate Content Detected" for i in issues)

    def test_unique_content_no_duplication(self, detector: IssueDetector) -> None:
        page_a = {"url": "https://example.com/a", "title": "About Us", "meta_description": "Learn about our company history and mission.", "h1": "About Our Company", "word_count": 500}
        page_b = {"url": "https://example.com/b", "title": "Contact Us", "meta_description": "Get in touch with our support team for help.", "h1": "Contact Information", "word_count": 200}
        detector.detect_duplication_issues([page_a, page_b])
        issues = detector.get_issues()
        assert not any(i["issue"] == "Duplicate Content Detected" for i in issues)


class TestExclusionPatterns:
    """_should_exclude: excluded URLs skipped, non-excluded checked."""

    def test_excluded_url_skipped(self) -> None:
        detector = IssueDetector(exclusion_patterns=["/admin/*"])
        result = {"url": "https://example.com/admin/dashboard", "title": "", "meta_description": "", "h1": "", "word_count": 10, "status_code": 200}
        detector.detect_issues(result)
        issues = detector.get_issues()
        assert len(issues) == 0

    def test_non_excluded_url_checked(self) -> None:
        detector = IssueDetector(exclusion_patterns=["/admin/*"])
        result = {"url": "https://example.com/blog/post", "title": "", "meta_description": "", "h1": "", "word_count": 50, "status_code": 200}
        detector.detect_issues(result)
        issues = detector.get_issues()
        assert any(i["issue"] == "Missing Title Tag" for i in issues)


class TestSecurityIssues:
    def test_missing_hsts(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'Missing HSTS Header' for i in issues)

    def test_has_hsts_no_warning(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {
            'strict-transport-security': 'max-age=31536000; includeSubDomains'
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any(i['issue'] == 'Missing HSTS Header' for i in issues)

    def test_missing_csp(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'Missing Content-Security-Policy' for i in issues)

    def test_missing_x_frame_options(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'Missing X-Frame-Options' for i in issues)

    def test_missing_x_content_type_options(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'Missing X-Content-Type-Options' for i in issues)

    def test_missing_referrer_policy(self, detector, basic_page_result):
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'Missing Referrer-Policy' for i in issues)

    def test_http_not_https_on_form_page(self, detector, basic_page_result):
        basic_page_result['url'] = 'http://example.com/login'
        basic_page_result['has_form'] = True
        basic_page_result['response_headers'] = {
            'strict-transport-security': 'max-age=31536000',
            'content-security-policy': "default-src 'self'",
            'x-frame-options': 'DENY',
            'x-content-type-options': 'nosniff',
            'referrer-policy': 'strict-origin-when-cross-origin',
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any(i['issue'] == 'HTTP Used on Form Page' for i in issues)


class TestStructuredDataAdvanced:
    def test_jsonld_missing_context(self, detector, basic_page_result):
        basic_page_result['json_ld'] = [{'@type': 'WebSite', 'name': 'Test'}]
        basic_page_result['schema_org'] = []
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Missing @context' in i['issue'] for i in issues)

    def test_jsonld_missing_type(self, detector, basic_page_result):
        basic_page_result['json_ld'] = [{'@context': 'https://schema.org', 'name': 'Test'}]
        basic_page_result['schema_org'] = []
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Missing @type' in i['issue'] for i in issues)

    def test_valid_jsonld_no_warning(self, detector, basic_page_result):
        # basic_page_result already has valid JSON-LD with @context and @type
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any('Missing @context' in i['issue'] for i in issues)
        assert not any('Missing @type' in i['issue'] for i in issues)


class TestSSLIssues:
    def test_http_page(self, detector, basic_page_result):
        basic_page_result['url'] = 'http://example.com/'
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('HTTP' in i['issue'] for i in issues)

    def test_https_page_no_warning(self, detector, basic_page_result):
        basic_page_result['url'] = 'https://example.com/'
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert not any('Page Served Over HTTP' in i['issue'] for i in issues)

    def test_http_form_page_gets_both(self, detector, basic_page_result):
        basic_page_result['url'] = 'http://example.com/login'
        basic_page_result['has_form'] = True
        basic_page_result['response_headers'] = {}
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        http_issues = [i for i in issues if 'HTTP' in i['issue']]
        assert len(http_issues) == 2


class TestCoreWebVitals:
    def test_images_without_dimensions(self, detector, basic_page_result):
        basic_page_result['cwv_signals'] = {
            'large_images_without_dimensions': 3, 'dom_element_count': 100,
            'missing_font_display': False, 'missing_preconnect': False,
            'inline_scripts_count': 0, 'inline_styles_count': 0, 'render_blocking_resources': 2,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Images Without Dimensions' in i['issue'] for i in issues)

    def test_large_dom(self, detector, basic_page_result):
        basic_page_result['cwv_signals'] = {
            'large_images_without_dimensions': 0, 'dom_element_count': 2000,
            'missing_font_display': False, 'missing_preconnect': False,
            'inline_scripts_count': 0, 'inline_styles_count': 0, 'render_blocking_resources': 2,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Large DOM Size' in i['issue'] for i in issues)

    def test_missing_font_display(self, detector, basic_page_result):
        basic_page_result['cwv_signals'] = {
            'large_images_without_dimensions': 0, 'dom_element_count': 100,
            'missing_font_display': True, 'missing_preconnect': False,
            'inline_scripts_count': 0, 'inline_styles_count': 0, 'render_blocking_resources': 2,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('font-display' in i['issue'] for i in issues)

    def test_many_render_blocking(self, detector, basic_page_result):
        basic_page_result['cwv_signals'] = {
            'large_images_without_dimensions': 0, 'dom_element_count': 100,
            'missing_font_display': False, 'missing_preconnect': False,
            'inline_scripts_count': 0, 'inline_styles_count': 0, 'render_blocking_resources': 8,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        assert any('Render-Blocking' in i['issue'] for i in issues)

    def test_no_cwv_issues_on_clean_page(self, detector, basic_page_result):
        basic_page_result['cwv_signals'] = {
            'large_images_without_dimensions': 0, 'dom_element_count': 200,
            'missing_font_display': False, 'missing_preconnect': False,
            'inline_scripts_count': 1, 'inline_styles_count': 1, 'render_blocking_resources': 3,
        }
        detector.detect_issues(basic_page_result)
        issues = detector.get_issues()
        cwv_issues = [i for i in issues if i['category'] == 'Performance' and 'Response' not in i['issue'] and 'Page Size' not in i['issue']]
        assert len(cwv_issues) == 0