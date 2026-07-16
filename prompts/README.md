# seocli Agent Prompt Templates

Pre-built prompt snippets to configure AI agents for using seocli.

| File | For |
|------|-----|
| `claude-code.md` | Claude Code (Anthropic) |
| `cursor.md` | Cursor IDE |
| `generic-mcp.md` | Any MCP-compatible agent |

## Usage

### Claude Code
Copy the content of `claude-code.md` into your `~/.claude/CLAUDE.md` or project `CLAUDE.md`.

### Cursor
Copy the content of `cursor.md` into your `.cursorrules` file.

### Other Agents
Use `generic-mcp.md` as a starting point. Customize the tool names and response format for your specific agent framework.

## Key Decision Rules

| Scenario | Tool |
|----------|------|
| Audit a site (<50 pages) | `seocli_audit` |
| Audit a large site (50+ pages) | `seocli_audit_start` → `seocli_audit_poll` → `seocli_audit_results` |
| Quick health check | Read `seocli://audit/score` or `seocli_issues_summary` |
| CI/CD pipeline | `seocli_audit --fail-on error` |
| SPA (React/Vue/Angular) | Add `enable_js: true` |