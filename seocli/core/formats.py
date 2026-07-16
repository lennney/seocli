"""Export crawl results to CSV, Markdown, and HTML formats."""
import csv
import io
from collections import defaultdict


def to_csv(results):
    """Export issues and pages to CSV. Returns dict with 'issues' and 'pages' CSV strings."""
    output = {}

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['URL', 'Type', 'Category', 'Issue', 'Details'])
    for issue in results.get('issues', []):
        writer.writerow([issue['url'], issue['type'], issue['category'],
                         issue['issue'], issue['details']])
    output['issues'] = buf.getvalue()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['URL', 'Status', 'Title', 'Meta Description', 'H1', 'Word Count',
                     'Internal Links', 'External Links', 'Response Time (ms)', 'Size (bytes)'])
    for page in results.get('pages', []):
        writer.writerow([
            page.get('url', ''), page.get('status_code', ''),
            page.get('title', ''), page.get('meta_description', ''),
            page.get('h1', ''), page.get('word_count', ''),
            page.get('internal_links', 0), page.get('external_links', 0),
            page.get('response_time', ''), page.get('size', ''),
        ])
    output['pages'] = buf.getvalue()

    return output


def to_markdown(results):
    """Export issues summary as Markdown report."""
    lines = [f"# SEO Audit Report: {results.get('url', '')}", ""]
    stats = results.get('stats', {})
    lines.append(f"**{stats.get('crawled', 0)} pages crawled** | "
                 f"{stats.get('discovered', 0)} discovered | "
                 f"depth: {stats.get('depth', 0)} | "
                 f"{stats.get('elapsed_seconds', 0)}s")
    lines.append("")

    issues = results.get('issues', [])
    if not issues:
        lines.append("✅ No issues found.")
        return "\n".join(lines)

    by_category = defaultdict(lambda: {'error': [], 'warning': [], 'info': []})
    for issue in issues:
        by_category[issue['category']][issue['type']].append(issue)

    for category in sorted(by_category):
        cats = by_category[category]
        total = len(cats['error']) + len(cats['warning']) + len(cats['info'])
        lines.append(f"## {category} ({total} issues)")
        lines.append("")
        for typ, emoji in [('error', '🔴'), ('warning', '🟡'), ('info', '🔵')]:
            for issue in cats[typ]:
                lines.append(f"- {emoji} **{issue['issue']}** — [{issue['url']}]({issue['url']})")
                lines.append(f"  {issue['details']}")
                lines.append("")
    return "\n".join(lines)


def to_html(results):
    """Export issues as a simple HTML report."""
    issues = results.get('issues', [])
    stats = results.get('stats', {})

    rows = ""
    for issue in issues:
        bg = {'error': '#fee', 'warning': '#ffe', 'info': '#eef'}.get(issue['type'], '#fff')
        rows += f"""<tr style="background:{bg}">
            <td><a href="{issue['url']}">{issue['url']}</a></td>
            <td>{issue['type']}</td>
            <td>{issue['category']}</td>
            <td>{issue['issue']}</td>
            <td>{issue['details']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>SEO Audit: {results.get('url', '')}</title>
<style>body{{font-family:system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#333;color:#fff}}</style></head>
<body>
<h1>SEO Audit Report: {results.get('url', '')}</h1>
<p>{stats.get('crawled', 0)} pages crawled, {stats.get('discovered', 0)} discovered, {stats.get('elapsed_seconds', 0)}s</p>
<h2>{len(issues)} Issues Found</h2>
<table><tr><th>URL</th><th>Type</th><th>Category</th><th>Issue</th><th>Details</th></tr>{rows}</table>
</body></html>"""
