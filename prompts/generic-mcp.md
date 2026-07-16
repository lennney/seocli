# seocli — Generic MCP Agent Prompt

For any MCP-compatible agent (OpenCode, Codex, Continue, etc.):

```
## SEO Audit Capability

You can audit websites for SEO issues using the seocli MCP server.

**Tools:**
| Tool | Use Case |
|------|----------|
| `seocli_audit` | Full crawl + detailed audit |
| `seocli_audit_start` | Start async crawl (returns session_id) |
| `seocli_audit_poll` | Get incremental results for session |
| `seocli_audit_results` | Get final results for session |
| `seocli_issues_summary` | Quick grouped issue overview |

**Resources:**
| URI | Returns |
|-----|---------|
| `seocli://audit/latest` | Most recent full audit result |
| `seocli://audit/score` | 0-100 health score + grade |

**When to use which:**
- Small site (<50 pages) → `seocli_audit`
- Large site (50+ pages) → `seocli_audit_start` + poll loop
- Just want a score → read `seocli://audit/score`
- Want latest cached result → read `seocli://audit/latest`

**Output format:** Structured JSON with `issues[]`, `pages[]`, `links[]`, `stats{}`.

**Issue categories:** SEO, Technical, Content, Mobile, Accessibility, Social, Structured Data, Performance, Indexability, Duplication, Security.

**Issue types:** error (must fix), warning (should fix), info (note).
```