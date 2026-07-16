# seocli — Cursor Integration Prompt

Add to your `.cursorrules` or workspace rules:

```
## SEO Audit

Use the seocli MCP server for website SEO audits:

### Tools
- `seocli_audit` — Full crawl + audit (synchronous)
- `seocli_audit_start` + `seocli_audit_poll` — Async incremental (large sites)
- `seocli_issues_summary` — Quick shallow audit
- `seocli://audit/score` — Resource: 0-100 health score

### When user says
- "audit this site" / "check SEO" → `seocli_audit`
- "quick SEO check" → `seocli_issues_summary`
- "how healthy is this site" → read `seocli://audit/score`
- "audit this big site" → `seocli_audit_start` + poll

### Response format
Group issues by category with emoji indicators.
Always include: pages crawled, issue count, top 3 issues.
```