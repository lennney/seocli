"""Crawl session manager for async/streaming MCP audits."""
import threading
import time
import uuid
from collections import defaultdict


class CrawlSessionManager:
    """Manages background crawl sessions for incremental MCP reporting."""

    def __init__(self):
        self._sessions = {}
        self._lock = threading.Lock()

    def start_session(self, crawler, url):
        """Start a new crawl session, return session_id."""
        session_id = str(uuid.uuid4())[:8]
        with self._lock:
            self._sessions[session_id] = {
                'crawler': crawler,
                'url': url,
                'started_at': time.time(),
                'last_poll_index': 0,  # index into issues list for incremental
                'status': 'running',
            }
        # Start crawl in background
        success, msg = crawler.crawl(url)
        if not success:
            with self._lock:
                self._sessions[session_id]['status'] = 'error'
                self._sessions[session_id]['error'] = msg
            return session_id

        # Start a background thread to wait for completion
        def _wait():
            crawler.wait()
            crawler.stop()
            with self._lock:
                if session_id in self._sessions:
                    self._sessions[session_id]['status'] = 'completed'

        t = threading.Thread(target=_wait, daemon=True)
        t.start()
        return session_id

    def poll_session(self, session_id):
        """Get incremental results since last poll. Returns dict with new_issues, progress, status."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return {'error': f'Session {session_id} not found'}

            crawler = session['crawler']
            all_issues = crawler.issue_detector.get_issues() if crawler.issue_detector else []
            last_idx = session['last_poll_index']

            new_issues = all_issues[last_idx:]
            session['last_poll_index'] = len(all_issues)

            stats = {
                'crawled': crawler.stats.get('crawled', 0),
                'discovered': crawler.link_manager.get_stats()['discovered'] if crawler.link_manager else 0,
                'elapsed_seconds': round(time.time() - session['started_at'], 1),
            }

            return {
                'session_id': session_id,
                'status': session['status'],
                'new_issues': new_issues,
                'total_issues': len(all_issues),
                'progress': stats,
            }

    def get_results(self, session_id):
        """Get final results for a completed session."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return {'error': f'Session {session_id} not found'}
            if session['status'] == 'running':
                return {'error': 'Session still running', 'session_id': session_id}

        return session['crawler'].get_results()

    def cleanup_session(self, session_id):
        """Remove a completed session."""
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_old_sessions(self, max_age_seconds=3600):
        """Remove sessions older than max_age_seconds."""
        now = time.time()
        with self._lock:
            stale = [
                sid for sid, s in self._sessions.items()
                if now - s['started_at'] > max_age_seconds
            ]
            for sid in stale:
                self._sessions.pop(sid, None)
