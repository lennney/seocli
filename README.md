# seocli — SEO Crawling & Auditing CLI for AI Agents

> **"审计一下 example.com 的 SEO"** → agent invokes `seocli`, returns structured issue report.

**seocli** is a dual-mode SEO auditing tool built for **AI agent integration**:

- **CLI mode** — `seocli https://example.com` → structured JSON on stdout
- **MCP mode** — tools for [Claude Code](https://claude.ai/code) and any MCP-compatible agent framework

Crawl any website, extract SEO data, detect issues, get actionable JSON output.

---

## Install

```bash
pip install seocli[js,mcp]

# Optional: JS rendering for SPAs
pip install playwright && playwright install chromium
```

---

## Quick Start

```bash
# Quick audit — JSON printed to stdout
seocli https://example.com --quiet

# Deep crawl with output file
seocli https://example.com --depth 5 --json report.json

# Local dev server (no delay)
seocli http://localhost:3000 --delay 0

# JavaScript-rendered SPA
seocli https://spa-site.com --js
```

---

## MCP Integration

seocli ships with an MCP server — register it in your agent's MCP configuration:

### Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "seocli": {
      "command": "python3",
      "args": ["-m", "seocli.server"]
    }
  }
}
```

Then restart Claude Code. These tools become available:

| Tool | Description |
|------|-------------|
| `seocli_audit` | Full crawl + audit. Returns pages, issues, links, stats as JSON. |
| `seocli_issues_summary` | Quick shallow crawl + grouped issue summary. Faster. |
| `seocli_audit_start` | Start async crawl (large sites). Returns `session_id` immediately. |
| `seocli_audit_poll` | Poll async session for incremental results + progress. |
| `seocli_audit_results` | Get final results of an async session. |
| `seocli://audit/latest` | Resource: most recent audit result as JSON. |
| `seocli://audit/score` | Resource: 0-100 site health score with letter grade. |

### Async Audits (Large Sites)

For sites with 50+ pages, use the async flow to avoid long blocking waits:

```
1. seocli_audit_start(url) → session_id
2. seocli_audit_poll(session_id) → incremental issues + progress
3. seocli_audit_results(session_id) → final report
```

### Agent Prompt Templates

Ready-to-use prompt snippets for AI agents: see [`prompts/`](prompts/) directory.

| File | For |
|------|-----|
| `prompts/claude-code.md` | Claude Code |
| `prompts/cursor.md` | Cursor IDE |
| `prompts/generic-mcp.md` | Any MCP agent |

### Any MCP Host

seocli uses the standard [Model Context Protocol](https://modelcontextprotocol.io) — it works with any MCP-compatible client. Just point your MCP host at `python3 -m seocli.server`.

### Agent Prompt Example

When configuring an agent to use seocli, describe it like this:

```
You have access to the `seocli_audit` MCP tool. When the user says
"audit example.com for SEO issues", call it with the URL. Parse the
`issues` array from the result and present:
- Errors first (🔴), grouped by category
- Warnings second (🟡), grouped by category
- Key stats: pages crawled, response time, issue count
```

---

## Agent Decision Guide

### When to use `--js`
- The site is a known SPA (React/Vue/Angular with client-side rendering)
- Tags don't appear in raw HTML: `curl <url>` returns no meta tags
- **Default**: no JS (faster, lighter, fewer dependencies)

### When to use `--delay`
- **Own/local site**: `--delay 0` (fastest, no artificial wait)
- **Other people's sites**: `--delay 1.0` at minimum (be polite)
- The delay is seconds between requests — `1.0` = 1 request/second

### When to use `--respect-robots`
- **Other people's sites**: keep enabled (default: on)
- **Own site** with restrictive robots.txt: use `--no-robots`

### Finding Priority (high → low)

| Priority | Type | Category | Example |
|----------|------|----------|---------|
| 🔴 1 | error | SEO | Missing title tag |
| 🔴 2 | error | Technical | 404, 5xx status codes |
| 🔴 3 | error | Indexability | noindex on critical pages |
| 🟡 4 | warning | SEO | Title too long/short |
| 🟡 5 | warning | Social | Missing OG/Twitter tags |
| 🟡 6 | warning | Technical | Missing canonical URL |
| 🔴 7 | error | Content | Broken image, missing alt text |
| 🟡 8 | warning | Content | Thin content (< 300 words) |
| 🟡 9 | warning | Performance | Slow page load (> 2s) |
| 🔵 10 | info | Technical | Redirect detected (verify) |

---

## JSON Output Structure

```json
{
  "url": "https://example.com",
  "stats": {
    "crawled": 42,
    "discovered": 85,
    "depth": 3,
    "speed": 5.2,
    "elapsed_seconds": 8.1
  },
  "pages": [
    {
      "url": "https://example.com/",
      "status_code": 200,
      "title": "Page Title",
      "meta_description": "Description...",
      "h1": "Heading",
      "h2": ["Subheading"],
      "word_count": 450,
      "lang": "en",
      "canonical_url": "...",
      "og_tags": { "og:title": "...", "og:description": "...", "og:image": "..." },
      "twitter_tags": { "twitter:card": "summary_large_image" },
      "json_ld": [{ "@type": "WebSite", ... }],
      "analytics": { "gtag": true, "ga4_id": "G-XXXXX" },
      "images": [{ "src": "...", "alt": "...", "width": "", "height": "" }],
      "hreflang": [{ "hreflang": "en", "href": "..." }],
      "internal_links": 15,
      "external_links": 3,
      "response_time": 234.5,
      "size": 12450,
      "viewport": "width=device-width, initial-scale=1",
      "robots": "index, follow",
      "is_internal": true,
      "depth": 0,
      "linked_from": ["https://example.com/other"]
    }
  ],
  "links": [
    {
      "source_url": "https://example.com/",
      "target_url": "https://example.com/about",
      "anchor_text": "About us",
      "is_internal": true,
      "target_domain": "example.com",
      "target_status": 200,
      "placement": "body"
    }
  ],
  "issues": [
    {
      "url": "https://example.com/page",
      "type": "error",
      "category": "SEO",
      "issue": "Missing Title Tag",
      "details": "Page has no title tag"
    }
  ]
}
```

---

## Issue Classification

### Issue Types

| Type | Meaning | Action |
|------|---------|--------|
| `error` | Must fix | Missing title, 404, noindex, broken images |
| `warning` | Should fix | Title too long/short, thin content, slow page |
| `info` | Note | Redirect detected, informative findings |

### Issue Categories

SEO · Technical · Content · Mobile · Accessibility · Social · Structured Data · Performance · Indexability · Duplication

---

## What's New in v0.4.0

### GEO (Generative Engine Optimization) — AI Search Readiness

First-of-its-kind GEO category: checks if pages are optimized for AI search engines (ChatGPT, Perplexity, Google AI Overviews). 8 new rules covering: AI crawler blocking, content structure for AI models, source citations, author attribution (E-E-A-T), publish dates, FAQ schema detection, and more.

### Custom Rules DSL

Define your own SEO checks in `.seocli-rules.yaml` — no Python code needed. 8 check types: field_exists, field_matches_regex, list_min_items, and more. URL include/exclude patterns via glob. See `.seocli-rules.example.yaml`.

### GitHub Action

Official CI/CD integration: auto-audit on PRs, comment results, fail on errors. See `.github/workflows/seo-audit.yml`.

### What's New in v0.3.0

### MCP Deepening — AI Agent Native

- **Async audits**: `seocli_audit_start` / `seocli_audit_poll` / `seocli_audit_results` — incremental reporting for large sites
- **MCP Resources**: `seocli://audit/score` (0-100 health score) and `seocli://audit/latest` (cached result)
- **Prompt templates**: Ready-to-use agent prompts for Claude Code, Cursor, and any MCP agent in `prompts/`

### What's New in v0.2.0

### New Rule Categories

| Category | New Rules | Type |
|----------|-----------|------|
| **Security** | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Page Served Over HTTP, HTTP on Form Pages | error |
| **Accessibility** | ARIA Landmarks, Positive Tabindex, Missing Skip Link, Potential Contrast Issues | error/warning |
| **Structured Data** | JSON-LD @context validation, @type validation, Schema.org itemtype | warning |
| **Performance** | Images Without Dimensions (CLS), Large DOM Size, Missing font-display, No Preconnect Hints, Render-Blocking Resources | warning/info |
| **SSL** | HTTPS usage check | error |

### New Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| JSON | `--format json` (default) | Structured JSON for AI agents and programmatic use |
| CSV | `--format csv` | Issues + Pages as CSV for spreadsheet analysis |
| Markdown | `--format markdown` | Human-readable report with emoji-coded issues |
| HTML | `--format html` | Standalone HTML report with styled table |

### CI/CD Integration

```bash
# Fail if any errors found (exit code 1)
seocli https://example.com --fail-on error

# Fail if any warnings or errors found
seocli https://example.com --fail-on warning
```

### Testing

seocli now includes a comprehensive test suite. Run with:

```bash
pip install seocli[dev]
python -m pytest tests/ -v
```

### Rule Count: 25 → 60+

v0.2.0 more than doubles the number of SEO audit rules from 25 to over 60, covering security headers, accessibility deep-dive, structured data quality, SSL/HTTPS, and Core Web Vitals static signals.

---

## CLI Usage

| Scenario | Command |
|----------|---------|
| Quick audit | `seocli https://example.com` |
| Quiet (agent) | `seocli https://example.com --quiet` |
| Save to file | `seocli https://example.com --json report.json` |
| Local dev | `seocli http://localhost:3000 --delay 0` |
| Polite crawl | `seocli https://other.com --delay 1.0 --respect-robots` |
| SPA audit | `seocli https://spa.com --js` |
| Deep crawl | `seocli https://big.com --depth 5 --max-urls 2000` |
| No duplication check | `seocli https://big.com --no-duplicate-check` |

---

## Options

```
seocli <url> [options]

positional:
  url                   Website URL to audit

options:
  --depth N             Max crawl depth (default: 3)
  --max-urls N          Max URLs to crawl (default: 500)
  --delay SECONDS       Seconds between requests (default: 0 = no limit)
  --js                  Enable JavaScript rendering (requires playwright)
  --respect-robots      Respect robots.txt (default: on)
  --no-robots           Ignore robots.txt
  --concurrency N       Max concurrent requests (default: 5)
  --json FILE           Save JSON output to file
  --quiet, -q           Suppress progress output
  --no-duplicate-check  Skip duplicate content detection (faster on large sites)
  --format {json,csv,markdown,md,html}   Output format (default: json)
  --fail-on {error,warning,info,none}    CI gate: exit 1 if issues at this level exist
  --rules FILE          Custom rules config (.yaml or .json)
  --help                Show this help
```

---

## Custom Rules

Define your own SEO checks in `.seocli-rules.yaml`:

```bash
# Run with custom rules
seocli https://example.com --rules .seocli-rules.yaml

# Example: check all product pages have >300 words
# See .seocli-rules.example.yaml for more examples
```

8 check types: `field_exists`, `field_not_empty`, `field_min_length`, `field_max_length`, `field_matches_regex`, `field_not_matches_regex`, `list_min_items`, `url_matches_pattern`. URL include/exclude patterns via glob.

### GitHub Action

```yaml
# .github/workflows/seo-audit.yml
# Auto-audits on PR, comments results, fails on errors
# See .github/workflows/seo-audit.yml
```

---

## Extras

### JS Rendering

```bash
pip install seocli[js]
playwright install chromium
seocli https://spa-site.com --js
```

### MCP Only

```bash
pip install seocli[mcp]
python -m seocli.server
```

---

## License

MIT
