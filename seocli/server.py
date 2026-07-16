#!/usr/bin/env python3
"""
seocli MCP server — exposes website auditing as an MCP tool.

Quick setup:
  pip install seocli[mcp]
  seocli setup                              # auto-registers in ~/.claude/mcp.json

Or manually register in ~/.claude/mcp.json:
{
  "mcpServers": {
    "seocli": {
      "command": "python3",
      "args": ["-m", "seocli.server"]
    }
  }
}

Then agent can call `seocli_audit` / `seocli_issues_summary` as tools
instead of shelling out.
"""
import json
from collections import Counter, defaultdict

from mcp.server.fastmcp import FastMCP
from seocli.crawl import Crawler
from seocli.core.session import CrawlSessionManager

mcp = FastMCP("seocli", instructions="SEO crawling & auditing — crawl any website and get structured SEO issue reports")

session_manager = CrawlSessionManager()

# Store latest audit result for resource access
_latest_audit_result = None


@mcp.resource("seocli://audit/latest")
def get_latest_audit() -> str:
    """Return the most recent audit result as a JSON resource. Agents can read this without running a tool."""
    global _latest_audit_result
    if _latest_audit_result is None:
        return json.dumps({"message": "No audit has been run yet. Use seocli_audit to start one."})
    return json.dumps(_latest_audit_result, indent=2, default=str, ensure_ascii=False)


@mcp.resource("seocli://audit/score")
def get_site_health_score() -> str:
    """Return a 0-100 site health score based on the latest audit. Agents use this for quick assessments."""
    global _latest_audit_result
    if _latest_audit_result is None:
        return json.dumps({"score": None, "message": "No audit data available"})

    issues = _latest_audit_result.get('issues', [])
    pages = _latest_audit_result.get('pages', [])
    stats = _latest_audit_result.get('stats', {})

    total_pages = max(stats.get('crawled', 1), 1)
    errors = sum(1 for i in issues if i['type'] == 'error')
    warnings = sum(1 for i in issues if i['type'] == 'warning')

    error_ratio = errors / max(total_pages, 1)
    warn_ratio = warnings / max(total_pages, 1)

    score = 100
    score -= min(error_ratio * 40, 40)
    score -= min(warn_ratio * 20, 30)

    pages_with_title = sum(1 for p in pages if p.get('title'))
    pages_with_desc = sum(1 for p in pages if p.get('meta_description'))
    if total_pages > 0:
        title_coverage = pages_with_title / total_pages
        desc_coverage = pages_with_desc / total_pages
        score += min(title_coverage * 10, 10)
        score += min(desc_coverage * 5, 5)

    score = max(0, min(100, round(score)))

    if score >= 90:
        grade = 'A'
    elif score >= 75:
        grade = 'B'
    elif score >= 60:
        grade = 'C'
    elif score >= 40:
        grade = 'D'
    else:
        grade = 'F'

    return json.dumps({
        'score': score,
        'grade': grade,
        'total_pages': total_pages,
        'errors': errors,
        'warnings': warnings,
        'info': sum(1 for i in issues if i['type'] == 'info'),
        'url': _latest_audit_result.get('url', ''),
    })


def _store_latest_result(result):
    """Store the latest audit result for resource access. Called by audit tools."""
    global _latest_audit_result
    _latest_audit_result = result


@mcp.tool(
    name="seocli_audit",
    description="Crawl a website and audit it for SEO issues. Returns structured JSON with pages, issues, links, and stats.",
)
def seocli_audit(
    url: str,
    max_depth: int = 3,
    max_urls: int = 500,
    delay: float = 0,
    respect_robots: bool = True,
    enable_js: bool = False,
    concurrency: int = 5,
    enable_duplication_check: bool = True,
) -> str:
    """
    Crawl and audit a website for SEO issues.

    Args:
        url: Website URL to audit (e.g., https://example.com)
        max_depth: Max crawl depth (default: 3)
        max_urls: Max URLs to crawl (default: 500)
        delay: Seconds between requests (default: 0 = no limit. Use 1.0+ for other people's sites)
        respect_robots: Respect robots.txt (default: True)
        enable_js: Enable JavaScript rendering (requires playwright installed)
        concurrency: Max concurrent requests (default: 5)
        enable_duplication_check: Detect duplicate content across pages (default: True, slower on large sites)

    Returns:
        JSON string with keys: url, stats, pages[], links[], issues[]
    """
    config = {
        'max_depth': max_depth,
        'max_urls': max_urls,
        'delay': delay,
        'respect_robots': respect_robots,
        'concurrency': concurrency,
        'enable_javascript': enable_js,
        'enable_duplication_check': enable_duplication_check,
        'discover_sitemaps': True,
    }

    crawler = Crawler(config)
    success, msg = crawler.crawl(url)

    if not success:
        return json.dumps({"error": msg})

    crawler.wait()
    crawler.stop()

    results = crawler.get_results()
    _store_latest_result(results)
    return json.dumps(results, indent=2, default=str, ensure_ascii=False)


@mcp.tool(
    name="seocli_issues_summary",
    description="Quick crawl + grouped SEO issue summary. Faster than full audit (shallower depth, no duplication check).",
)
def seocli_issues_summary(
    url: str,
    max_urls: int = 50,
    delay: float = 0,
    respect_robots: bool = True,
) -> str:
    """
    Quick audit — crawl a limited set of pages and return a grouped issue summary.

    Args:
        url: Website URL to audit
        max_urls: Max URLs to crawl (default: 50)
        delay: Seconds between requests (default: 0)
        respect_robots: Respect robots.txt (default: True)

    Returns:
        JSON with summary: total_issues, by_category, top_issues
    """
    config = {
        'max_depth': 2,
        'max_urls': max_urls,
        'delay': delay,
        'respect_robots': respect_robots,
        'concurrency': 5,
        'enable_javascript': False,
        'enable_duplication_check': False,
        'discover_sitemaps': True,
    }

    crawler = Crawler(config)
    crawler.crawl(url)
    crawler.wait()
    crawler.stop()

    results = crawler.get_results()
    _store_latest_result(results)
    issues = results['issues']

    by_category = defaultdict(lambda: {'error': 0, 'warning': 0, 'info': 0})
    for i in issues:
        cat = i['category']
        by_category[cat][i['type']] += 1

    top = sorted(issues, key=lambda x: (0 if x['type'] == 'error' else 1, x['category']))[:10]

    summary = {
        'url': url,
        'total_issues': len(issues),
        'pages_crawled': results['stats']['crawled'],
        'by_category': dict(by_category),
        'top_issues': [
            {'url': i['url'], 'type': i['type'], 'category': i['category'],
             'issue': i['issue'], 'details': i['details']}
            for i in top
        ],
    }

    return json.dumps(summary, indent=2, default=str, ensure_ascii=False)


@mcp.tool(
    name="seocli_audit_start",
    description="Start an async SEO audit. Returns a session_id immediately. Use seocli_audit_poll to get incremental results.",
)
def seocli_audit_start(
    url: str,
    max_depth: int = 3,
    max_urls: int = 500,
    delay: float = 0,
    respect_robots: bool = True,
    enable_js: bool = False,
    concurrency: int = 5,
) -> str:
    """
    Start an async crawl. Returns session_id for polling.

    Args:
        url: Website URL to audit (e.g., https://example.com)
        max_depth: Max crawl depth (default: 3)
        max_urls: Max URLs to crawl (default: 500)
        delay: Seconds between requests (default: 0 = no limit. Use 1.0+ for other people's sites)
        respect_robots: Respect robots.txt (default: True)
        enable_js: Enable JavaScript rendering (requires playwright installed)
        concurrency: Max concurrent requests (default: 5)

    Returns:
        JSON string with session_id. Poll with seocli_audit_poll for incremental results.
    """
    import json

    config = {
        'max_depth': max_depth,
        'max_urls': max_urls,
        'delay': delay,
        'respect_robots': respect_robots,
        'concurrency': concurrency,
        'enable_javascript': enable_js,
        'enable_duplication_check': True,
        'discover_sitemaps': True,
    }

    crawler = Crawler(config)
    session_id = session_manager.start_session(crawler, url)

    return json.dumps({
        'session_id': session_id,
        'url': url,
        'message': f'Audit started. Poll with session_id={session_id}',
    })


@mcp.tool(
    name="seocli_audit_poll",
    description="Poll an active async audit for incremental results. Returns new issues found since last poll.",
)
def seocli_audit_poll(session_id: str) -> str:
    """
    Poll a running session for new issues and progress.

    Args:
        session_id: Session ID returned by seocli_audit_start

    Returns:
        JSON with session_id, status, new_issues[], total_issues, progress{crawled,discovered,elapsed_seconds}
    """
    import json
    result = session_manager.poll_session(session_id)
    return json.dumps(result, indent=2, default=str, ensure_ascii=False)


@mcp.tool(
    name="seocli_audit_results",
    description="Get final results for a completed async audit session.",
)
def seocli_audit_results(session_id: str) -> str:
    """
    Get final results for a completed session.

    Args:
        session_id: Session ID returned by seocli_audit_start

    Returns:
        JSON with full results (pages, links, issues, stats) — same format as seocli_audit.
    """
    import json
    result = session_manager.get_results(session_id)
    return json.dumps(result, indent=2, default=str, ensure_ascii=False)


def main():
    """Entry point for MCP server."""
    mcp.run()


if __name__ == '__main__':
    main()
