"""Custom rules DSL engine for user-defined SEO checks."""
import json
import os
import re
from fnmatch import fnmatch


class CustomRuleEngine:
    """Loads and executes user-defined SEO rules from YAML/JSON config."""

    SUPPORTED_CHECKS = {
        'field_exists': '_check_field_exists',
        'field_not_empty': '_check_field_not_empty',
        'field_min_length': '_check_field_min_length',
        'field_max_length': '_check_field_max_length',
        'field_matches_regex': '_check_field_matches_regex',
        'field_not_matches_regex': '_check_field_not_matches_regex',
        'list_min_items': '_check_list_min_items',
        'url_matches_pattern': '_check_url_matches_pattern',
    }

    def __init__(self, rules_config=None):
        """Initialize with optional rules list or file path."""
        self.rules = []
        if rules_config:
            if isinstance(rules_config, str):
                self.load_file(rules_config)
            elif isinstance(rules_config, list):
                self.rules = rules_config

    def load_file(self, filepath):
        """Load rules from .seocli-rules.yaml or .seocli-rules.json."""
        if not os.path.exists(filepath):
            return

        with open(filepath) as f:
            if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                try:
                    import yaml
                    config = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML required for .yaml rules. Install: pip install pyyaml")
            else:
                config = json.load(f)

        if isinstance(config, dict) and 'rules' in config:
            self.rules = config['rules']
        elif isinstance(config, list):
            self.rules = config

    def check(self, result):
        """Run all custom rules against a page result. Returns list of issues."""
        issues = []
        for rule in self.rules:
            url_matches = self._url_matches(result.get('url', ''), rule)
            if not url_matches:
                continue

            check_type = rule.get('check')
            if check_type not in self.SUPPORTED_CHECKS:
                continue

            handler = getattr(self, self.SUPPORTED_CHECKS[check_type])
            passed, detail = handler(result, rule)

            if not passed:
                issues.append({
                    'url': result.get('url', ''),
                    'type': rule.get('severity', 'warning'),
                    'category': rule.get('category', 'Custom'),
                    'issue': rule.get('name', check_type),
                    'details': detail or rule.get('message', f'Custom rule failed: {check_type}'),
                })

        return issues

    def _url_matches(self, url, rule):
        """Check if URL matches the rule's include/exclude patterns."""
        include = rule.get('include_urls', ['*'])
        exclude = rule.get('exclude_urls', [])

        for pattern in exclude:
            if fnmatch(url, pattern):
                return False

        for pattern in include:
            if fnmatch(url, pattern):
                return True
        return False

    def _get_value(self, result, rule):
        """Get a value from the result dict by field path (supports dot notation)."""
        field = rule.get('field', '')
        value = result
        for key in field.split('.'):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            if value is None:
                return None
        return value

    def _check_field_exists(self, result, rule):
        """Check that a field exists and is not None."""
        value = self._get_value(result, rule)
        passed = value is not None and value != ''
        msg = rule.get('message', f'{rule["field"]} is missing or empty')
        return passed, msg

    def _check_field_not_empty(self, result, rule):
        """Check that a field is not empty (truthy)."""
        value = self._get_value(result, rule)
        passed = bool(value)
        msg = rule.get('message', f'{rule["field"]} is empty')
        return passed, msg

    def _check_field_min_length(self, result, rule):
        """Check that a field's length (str/list) or value (int) >= min_value."""
        value = self._get_value(result, rule)
        min_val = rule.get('min_value', 0)
        if isinstance(value, int) and not isinstance(value, bool):
            passed = value >= min_val
            got = value
        else:
            passed = isinstance(value, (str, list)) and len(value) >= min_val
            got = len(value) if value else 0
        msg = rule.get('message', f'{rule["field"]} is too short (min {min_val}, got {got})')
        return passed, msg

    def _check_field_max_length(self, result, rule):
        """Check that a field's length (str/list) or value (int) <= max_value."""
        value = self._get_value(result, rule)
        max_val = rule.get('max_value', 999)
        if isinstance(value, int) and not isinstance(value, bool):
            passed = value <= max_val
            got = value
        else:
            passed = isinstance(value, (str, list)) and len(value) <= max_val
            got = len(value) if value else 0
        msg = rule.get('message', f'{rule["field"]} is too long (max {max_val}, got {got})')
        return passed, msg

    def _check_field_matches_regex(self, result, rule):
        """Check that a field matches a regex pattern."""
        value = self._get_value(result, rule)
        pattern = rule.get('pattern', '')
        passed = bool(value) and bool(re.search(pattern, str(value)))
        msg = rule.get('message', f'{rule["field"]} does not match pattern {pattern}')
        return passed, msg

    def _check_field_not_matches_regex(self, result, rule):
        """Check that a field does NOT match a regex pattern."""
        value = self._get_value(result, rule)
        pattern = rule.get('pattern', '')
        passed = not bool(value) or not re.search(pattern, str(value))
        msg = rule.get('message', f'{rule["field"]} should not match pattern {pattern}')
        return passed, msg

    def _check_list_min_items(self, result, rule):
        """Check that a list field has at least min_value items."""
        value = self._get_value(result, rule)
        min_val = rule.get('min_value', 1)
        passed = isinstance(value, list) and len(value) >= min_val
        msg = rule.get('message', f'{rule["field"]} has fewer than {min_val} items')
        return passed, msg

    def _check_url_matches_pattern(self, result, rule):
        """Check that the page URL matches a pattern."""
        url = result.get('url', '')
        pattern = rule.get('pattern', '')
        passed = bool(re.search(pattern, url))
        msg = rule.get('message', f'URL does not match pattern {pattern}')
        return passed, msg
