"""Tests for crawl session manager."""
import pytest
from seocli.core.session import CrawlSessionManager


class TestCrawlSessionManager:
    def test_poll_nonexistent_session(self):
        mgr = CrawlSessionManager()
        result = mgr.poll_session('nonexistent')
        assert 'not found' in result['error']

    def test_get_results_nonexistent_session(self):
        mgr = CrawlSessionManager()
        result = mgr.get_results('nonexistent')
        assert 'not found' in result['error']

    def test_cleanup_nonexistent_does_not_error(self):
        mgr = CrawlSessionManager()
        mgr.cleanup_session('nonexistent')

    def test_cleanup_old_sessions(self):
        mgr = CrawlSessionManager()
        # Add a fake session with old timestamp
        import time
        with mgr._lock:
            mgr._sessions['old'] = {
                'crawler': None,
                'url': 'https://example.com',
                'started_at': time.time() - 7200,
                'last_poll_index': 0,
                'status': 'completed',
            }
        mgr.cleanup_old_sessions(max_age_seconds=3600)
        assert 'old' not in mgr._sessions

    def test_recent_session_not_cleaned(self):
        mgr = CrawlSessionManager()
        import time
        with mgr._lock:
            mgr._sessions['recent'] = {
                'crawler': None,
                'url': 'https://example.com',
                'started_at': time.time() - 100,
                'last_poll_index': 0,
                'status': 'running',
            }
        mgr.cleanup_old_sessions(max_age_seconds=3600)
        assert 'recent' in mgr._sessions
