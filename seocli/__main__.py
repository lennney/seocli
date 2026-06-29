#!/usr/bin/env python3
"""
seocli — SEO crawling & auditing CLI

Audit any website for SEO issues:
  - Extracts title, meta description, headings, OG/Twitter/JSON-LD
  - Detects issues: missing title, 404s, broken images, duplicate content, slow pages
  - Supports JavaScript rendering for SPAs (--js, requires playwright)
  - Respects robots.txt and rate limits for polite crawling

Usage:
  seocli setup                                    # Auto-configure MCP
  seocli https://example.com                      # Quick audit
  seocli https://example.com --depth 5            # Deep crawl
  seocli http://localhost:3000 --delay 0          # Local dev
  seocli https://example.com --js                  # JS-rendered SPA
"""
import argparse
import json
import sys
import os


MCP_CONFIG = {
    "seocli": {
        "command": "python3",
        "args": ["-m", "seocli.server"],
    }
}


def cmd_setup():
    """Auto-configure MCP in ~/.claude/mcp.json, install extras."""
    mcp_path = os.path.expanduser("~/.claude/mcp.json")

    # 1. Configure MCP
    try:
        if os.path.exists(mcp_path):
            with open(mcp_path) as f:
                cfg = json.load(f)
        else:
            cfg = {"mcpServers": {}}
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Can't read {mcp_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if "seocli" in cfg.get("mcpServers", {}):
        print(f"ℹ️  seocli already registered in {mcp_path}", file=sys.stderr)
    else:
        cfg.setdefault("mcpServers", {})["seocli"] = MCP_CONFIG["seocli"]
        try:
            os.makedirs(os.path.dirname(mcp_path), exist_ok=True)
            with open(mcp_path, "w") as f:
                json.dump(cfg, f, indent=2)
            print(f"✅ seocli registered in {mcp_path}", file=sys.stderr)
        except OSError as e:
            print(f"❌ Can't write {mcp_path}: {e}", file=sys.stderr)
            sys.exit(1)

    # 2. Check optional extras
    missing = []
    try:
        import playwright  # noqa: F401
    except ImportError:
        missing.append("JS rendering (playwright)")
    try:
        import mcp  # noqa: F401
    except ImportError:
        missing.append("MCP server (mcp)")

    if missing:
        print(f"\n💡 Optional extras not installed:", file=sys.stderr)
        for m in missing:
            print(f"   • {m}", file=sys.stderr)
        print(f"\n   Install: pip install seocli[js,mcp]", file=sys.stderr)
    else:
        print(f"\n✅ All optional extras ready", file=sys.stderr)

    print(f"\n🚀 Done! Restart your AI assistant, then try:", file=sys.stderr)
    print(f'   "审计一下 example.com 的 SEO"', file=sys.stderr)


def cmd_audit(args):
    """Run a full crawl + SEO audit."""
    if not args.quiet:
        print(f"🔍 seocli — auditing: {args.url}", file=sys.stderr)
        if args.js:
            print("   ⚡ JavaScript rendering enabled", file=sys.stderr)

    config = {
        'max_depth': args.depth,
        'max_urls': args.max_urls,
        'delay': args.delay,
        'respect_robots': not args.no_robots,
        'concurrency': args.concurrency,
        'enable_javascript': args.js,
        'enable_duplication_check': not args.no_duplicate_check,
        'discover_sitemaps': True,
    }

    from seocli.crawl import Crawler

    crawler = Crawler(config)
    success, msg = crawler.crawl(args.url)

    if not success:
        print(json.dumps({'error': msg}), file=sys.stderr)
        sys.exit(1)

    # Progress indicator
    if not args.quiet and args.delay == 0:
        import threading
        import time as _time

        def _progress():
            while crawler.is_running:
                n = len(crawler.crawl_results)
                s = crawler.link_manager.get_stats()['discovered'] if crawler.link_manager else 0
                print(f"   📄 {n} crawled, {s} discovered", file=sys.stderr, end='\r')
                _time.sleep(0.5)
            print(f"   📄 {len(crawler.crawl_results)} crawled total", file=sys.stderr)
        t = threading.Thread(target=_progress, daemon=True)
        t.start()

    crawler.wait()
    crawler.stop()

    results = crawler.get_results()

    # Summarize for terminal
    if not args.quiet:
        s = results['stats']
        print(f"\n✅ Done — crawled {s['crawled']} pages, {s['discovered']} discovered, depth {s['depth']}", file=sys.stderr)
        by_cat = {}
        for issue in results['issues']:
            cat = issue['category']
            if cat not in by_cat:
                by_cat[cat] = {'errors': 0, 'warnings': 0, 'infos': 0}
            typ = issue['type']
            if typ in by_cat[cat]:
                by_cat[cat][typ] += 1
        if by_cat:
            print(f"\n🔴 Issues found:", file=sys.stderr)
            for cat, counts in sorted(by_cat.items()):
                parts = []
                if counts['errors']:
                    parts.append(f"{counts['errors']}🔴")
                if counts['warnings']:
                    parts.append(f"{counts['warnings']}🟡")
                if counts['infos']:
                    parts.append(f"{counts['infos']}🔵")
                if parts:
                    print(f"   {cat}: {' '.join(parts)}", file=sys.stderr)

    # Output JSON
    output = json.dumps(results, indent=2, default=str, ensure_ascii=False)
    if args.json:
        with open(args.json, 'w') as f:
            f.write(output)
        if not args.quiet:
            print(f"\n📁 Saved to: {args.json}", file=sys.stderr)
    else:
        print(output)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Route: `seocli setup` → setup command
    if argv and argv[0] == 'setup':
        cmd_setup()
        return

    # Otherwise → audit command
    parser = argparse.ArgumentParser(
        prog='seocli',
        description='SEO crawling & auditing CLI — crawl any website and get structured SEO issue reports.',
        epilog=(
            'Commands:\n'
            '  seocli setup                                  Auto-configure MCP\n'
            '  seocli <url> [options]                        Audit a website\n'
            '\nExamples:\n'
            '  seocli setup\n'
            '  seocli https://example.com\n'
            '  seocli http://localhost:3000 --delay 0\n'
            '  seocli https://example.com --js --json report.json\n'
            '  seocli https://example.com --depth 5 --respect-robots --delay 1.0\n'
            '\nAgent usage: Parse the JSON output\'s "issues" array for actionable findings.\n'
            'Each issue has: url, type (error/warning/info), category, issue, details.\n'
            'Group by category to produce a summary for the user.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('url', help='Website URL to audit (or "setup" to configure)')
    parser.add_argument('--depth', type=int, default=3, help='Max crawl depth (default: 3)')
    parser.add_argument('--max-urls', type=int, default=500, help='Max URLs to crawl (default: 500)')
    parser.add_argument('--delay', type=float, default=0,
                        help='Seconds between requests (default: 0 = no limit. Use 1.0 for other people\'s sites)')
    parser.add_argument('--js', action='store_true', help='Enable JavaScript rendering via Playwright (requires: pip install playwright && playwright install chromium)')
    parser.add_argument('--respect-robots', action='store_true', default=True, help='Respect robots.txt (default: on)')
    parser.add_argument('--no-robots', action='store_true', help='Ignore robots.txt')
    parser.add_argument('--concurrency', type=int, default=5, help='Max concurrent requests (default: 5)')
    parser.add_argument('--json', metavar='FILE', help='Output JSON to file (default: print to stdout)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output, only print final JSON')
    parser.add_argument('--no-duplicate-check', action='store_true', help='Skip duplicate content detection (O(n²), slower on large sets)')

    args = parser.parse_args(argv)
    cmd_audit(args)


if __name__ == '__main__':
    main()
