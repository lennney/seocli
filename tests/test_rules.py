"""Tests for custom rules DSL engine."""
import os
import json
import tempfile
import pytest
from seocli.core.rules import CustomRuleEngine


@pytest.fixture
def sample_page_result():
    return {
        'url': 'https://example.com/product/123',
        'title': 'Product Page Title',
        'meta_description': 'A great product description here that is long enough for testing purposes and covers all the features.',
        'word_count': 150,
        'viewport': '',
        'meta_tags': {
            'generator': 'React',
            'viewport': '',
        },
        'h2': ['Features', 'Specifications'],
        'og_tags': {},
        'twitter_tags': {},
    }


class TestCustomRuleEngine:
    def test_field_exists_passes(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Title exists', 'check': 'field_exists',
            'field': 'title', 'severity': 'error', 'category': 'Custom',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 0

    def test_field_exists_fails(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Missing field', 'check': 'field_exists',
            'field': 'non_existent_field', 'severity': 'error', 'category': 'Custom',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 1
        assert issues[0]['issue'] == 'Missing field'

    def test_field_min_length_fails(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Too short', 'check': 'field_min_length',
            'field': 'word_count', 'min_value': 300, 'severity': 'warning', 'category': 'Content',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 1
        assert 'Too short' in issues[0]['issue']

    def test_field_min_length_passes(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Long enough', 'check': 'field_min_length',
            'field': 'word_count', 'min_value': 100, 'severity': 'warning', 'category': 'Content',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 0

    def test_url_pattern_include(self):
        result = {'url': 'https://example.com/product/abc', 'title': 'Product ABC'}
        engine = CustomRuleEngine([{
            'name': 'Product check', 'check': 'field_exists',
            'field': 'title', 'severity': 'error', 'category': 'Custom',
            'include_urls': ['*/product/*'],
        }])
        issues = engine.check(result)
        assert len(issues) == 0  # title exists, rule matches URL

    def test_url_pattern_exclude(self):
        result = {'url': 'https://example.com/admin/dashboard'}
        engine = CustomRuleEngine([{
            'name': 'Admin check', 'check': 'field_exists',
            'field': 'non_existent', 'severity': 'error', 'category': 'Custom',
            'include_urls': ['*'],
            'exclude_urls': ['*/admin/*'],
        }])
        issues = engine.check(result)
        assert len(issues) == 0  # excluded by URL pattern

    def test_field_matches_regex(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'React detected', 'check': 'field_matches_regex',
            'field': 'meta_tags.generator', 'pattern': 'React',
            'severity': 'info', 'category': 'Custom',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 0  # 'React' found in generator

    def test_field_not_matches_regex(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'No spammy keywords', 'check': 'field_not_matches_regex',
            'field': 'title', 'pattern': '(?i)buy now|click here|free',
            'severity': 'warning', 'category': 'Content',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 0

    def test_list_min_items(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Need 3 H2s', 'check': 'list_min_items',
            'field': 'h2', 'min_value': 3, 'severity': 'warning', 'category': 'Content',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 1  # only 2 H2s

    def test_load_from_json_file(self, sample_page_result):
        rules = [{'name': 'Json rule', 'check': 'field_exists', 'field': 'title',
                   'severity': 'error', 'category': 'Custom'}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'rules': rules}, f)
            tmp = f.name
        try:
            engine = CustomRuleEngine(tmp)
            issues = engine.check(sample_page_result)
            assert len(issues) == 0  # title exists
        finally:
            os.unlink(tmp)

    def test_unknown_check_skipped(self, sample_page_result):
        engine = CustomRuleEngine([{
            'name': 'Unknown', 'check': 'non_existent_check',
            'field': 'title', 'severity': 'error', 'category': 'Custom',
        }])
        issues = engine.check(sample_page_result)
        assert len(issues) == 0  # silently skipped
