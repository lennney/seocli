"""Tests for CSV, Markdown, HTML exporters."""
import pytest

from seocli.core.formats import to_csv, to_markdown, to_html


@pytest.fixture
def sample_results():
    """A minimal crawl result with 2 issues for format testing."""
    return {
        'url': 'https://example.com',
        'stats': {'crawled': 10, 'discovered': 15, 'depth': 2, 'elapsed_seconds': 5.2},
        'pages': [
            {'url': 'https://example.com/', 'status_code': 200, 'title': 'Home',
             'meta_description': 'Home page desc', 'h1': 'Welcome', 'word_count': 500,
             'internal_links': 5, 'external_links': 2, 'response_time': 150.0, 'size': 12000},
            {'url': 'https://example.com/about', 'status_code': 200, 'title': 'About',
             'meta_description': 'About page desc', 'h1': 'About Us', 'word_count': 300,
             'internal_links': 3, 'external_links': 0, 'response_time': 200.0, 'size': 8000},
        ],
        'links': [],
        'issues': [
            {'url': 'https://example.com/', 'type': 'error', 'category': 'SEO',
             'issue': 'Missing Title Tag', 'details': 'Page has no title tag'},
            {'url': 'https://example.com/about', 'type': 'warning', 'category': 'Performance',
             'issue': 'Moderate Response Time', 'details': 'Page took 200ms'},
        ],
    }


class TestCsvExport:
    def test_csv_has_headers(self, sample_results):
        csv_data = to_csv(sample_results)
        assert 'URL,Type,Category,Issue,Details' in csv_data['issues']
        assert 'URL,Status,Title,Meta Description' in csv_data['pages']

    def test_csv_contains_issues(self, sample_results):
        csv_data = to_csv(sample_results)
        assert 'Missing Title Tag' in csv_data['issues']
        assert 'Moderate Response Time' in csv_data['issues']

    def test_csv_contains_pages(self, sample_results):
        csv_data = to_csv(sample_results)
        assert 'https://example.com/' in csv_data['pages']
        assert 'https://example.com/about' in csv_data['pages']


class TestMarkdownExport:
    def test_markdown_has_title(self, sample_results):
        md = to_markdown(sample_results)
        assert '# SEO Audit Report' in md

    def test_markdown_has_stats(self, sample_results):
        md = to_markdown(sample_results)
        assert '10 pages crawled' in md

    def test_markdown_contains_issues(self, sample_results):
        md = to_markdown(sample_results)
        assert 'Missing Title Tag' in md
        assert 'Moderate Response Time' in md

    def test_markdown_no_issues_message(self):
        results = {
            'url': 'https://example.com',
            'stats': {'crawled': 1, 'discovered': 1, 'depth': 1, 'elapsed_seconds': 1.0},
            'pages': [], 'links': [], 'issues': [],
        }
        md = to_markdown(results)
        assert 'No issues found' in md


class TestHtmlExport:
    def test_html_has_doctype(self, sample_results):
        html = to_html(sample_results)
        assert '<!DOCTYPE html>' in html

    def test_html_contains_issues(self, sample_results):
        html = to_html(sample_results)
        assert 'Missing Title Tag' in html
        assert 'Moderate Response Time' in html

    def test_html_has_stats(self, sample_results):
        html = to_html(sample_results)
        assert '10 pages crawled' in html
