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

Then restart Claude Code. Two tools become available:

| Tool | Description |
|------|-------------|
| `seocli_audit` | Full crawl + audit. Returns pages, issues, links, stats as JSON. |
| `seocli_issues_summary` | Quick shallow crawl + grouped issue summary. Faster. |

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
  --help                Show this help
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

---

## Review Module (formerly seo-review-board)

The `review/` directory contains the multi-agent SEO review framework, merged from the now-archived `seo-review-board` repository.

### What's Inside

| Path | Description |
|---|---|
| `review/SKILL.md` | Skill definition for multi-agent review |
| `review/roles/` | Reviewer role definitions (library, etc.) |
| `review/scenarios/` | Review scenarios: tech-review, seo-content-review, product-review |
| `review/adapters/` | Platform adapters: claude-code, codex, hermes |
| `review/references/` | Checklists & templates: scoring, PRD, document-consistency, etc. |
| `review/install.sh` | Installation script |

### Usage

```bash
# The review framework integrates with seocli as a sub-module.
# Use the SKILL.md in review/ to set up multi-agent review sessions.
# See review/REVIEW_BOARD_README.md for full documentation.
```

> **Note**: This module was migrated from `lennney/seo-review-board` (archived).
