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

mcp = FastMCP("seocli", instructions="SEO crawling & auditing — crawl any website and get structured SEO issue reports")


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


def main():
    """Entry point for MCP server."""
    mcp.run()


if __name__ == '__main__':
    main()
