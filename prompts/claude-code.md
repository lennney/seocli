# seocli — Claude Code Integration Prompt

Add this to your `~/.claude/CLAUDE.md` or project `CLAUDE.md`:

```markdown
## SEO Audit Tools

You have access to the seocli MCP tools for website SEO auditing.

### Blocking Audit (small sites, <50 pages)
Use `seocli_audit` for quick audits. Parse the `issues` array:
- **🔴 Errors first** (group by category: SEO, Security, Performance, etc.)
- **🟡 Warnings second** (group by category)
- **🔵 Info last**
- Present stats: pages crawled, elapsed time, issue count

### Async Audit (large sites, 50+ pages)
1. Call `seocli_audit_start` with the URL → get `session_id`
2. Poll with `seocli_audit_poll` every 5-10 seconds
3. Report incremental issues as they come in
4. Call `seocli_audit_results` for the final report

### Quick Summary
Use `seocli_issues_summary` for a fast overview (shallow crawl, grouped issues).

### Site Health
Read `seocli://audit/score` resource for a 0-100 health score with letter grade.

### Decision Guide
- **--js**: Use for SPAs (React/Vue/Angular). Default: no JS (faster).
- **--delay 1.0**: Use for other people's sites. Default: 0 (own sites).
- **--respect-robots**: Keep enabled for external sites.
- **--fail-on error**: Use in CI/CD to block deploys on SEO errors.

### Issue Priority (presentation order)
| Priority | Type | Example |
|----------|------|---------|
| 🔴 P0 | error: SEO, Indexability | Missing title, noindex on critical pages |
| 🔴 P1 | error: Technical, Security | 404s, missing HSTS, HTTP on forms |
| 🔴 P2 | error: Content, Accessibility | Broken images, contrast issues |
| 🟡 P3 | warning: SEO | Title too long/short, thin content |
| 🟡 P4 | warning: Social, Performance | Missing OG tags, slow pages, CWV signals |
| 🔵 P5 | info | Redirects, preconnect hints |
```