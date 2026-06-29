# seocli — AI 智能体专用 SEO 审计 CLI

> **"审计一下 example.com 的 SEO 问题"** → 智能体调用 `seocli`，返回结构化的问题报告。

**seocli** 是一个双模式 SEO 审计工具，专为 **AI 智能体集成**而设计：

- **CLI 模式** — `seocli https://example.com` → 结构化 JSON 输出到 stdout
- **MCP 模式** — 为 [Claude Code](https://claude.ai/code) 及所有兼容 MCP 的智能体框架提供工具接口

爬取任意网站，提取 SEO 数据，检测问题，输出可直接解析的 JSON 报告。

---

## 安装

```bash
pip install seocli[js,mcp]

# 可选：JS 渲染支持（用于 SPA 站点）
pip install playwright && playwright install chromium
```

---

## 快速开始

```bash
# 快速审计 — JSON 输出到 stdout
seocli https://example.com --quiet

# 深度爬取 + 保存到文件
seocli https://example.com --depth 5 --json report.json

# 本地开发服务器（无延迟）
seocli http://localhost:3000 --delay 0

# JavaScript 渲染的 SPA
seocli https://spa-site.com --js
```

---

## MCP 集成

seocli 内置 MCP 服务器，将其注册到智能体的 MCP 配置中即可使用：

### Claude Code

添加到 `~/.claude/mcp.json`：

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

重启 Claude Code 后，两个工具可用：

| 工具 | 描述 |
|------|------|
| `seocli_audit` | 完整爬取 + 审计。返回 pages、issues、links、stats 结构化 JSON |
| `seocli_issues_summary` | 快速浅层爬取 + 分组问题摘要。速度更快 |

### 任何 MCP 主机

seocli 使用标准 [Model Context Protocol](https://modelcontextprotocol.io) 协议，可与任何 MCP 兼容客户端配合使用。只需将 MCP 主机指向 `python3 -m seocli.server`。

### 智能体调用示例

配置智能体使用 seocli 时，可以这样描述：

```
你拥有 seocli_audit MCP 工具。当用户说"审计一下 example.com 的 SEO 问题"时，
调用该工具并传入 URL。解析返回结果中的 issues 数组，按以下顺序呈现：
- 首先是错误（🔴），按分类分组
- 然后是警告（🟡），按分类分组
- 最后是核心统计：爬取页数、响应时间、问题总数
```

---

## 智能体决策指南

### 何时使用 `--js`
- 已知是 SPA 站点（React/Vue/Angular 客户端渲染）
- 原始 HTML 中没有 meta 标签：`curl <url>` 看不到标题和描述
- **默认**：不启用 JS（更快、更轻量、依赖更少）

### 何时使用 `--delay`
- **自有/本地站点**：`--delay 0`（最快，无需等待）
- **他人站点**：至少 `--delay 1.0`（保持礼貌）
- 延迟值是请求间隔秒数 — `1.0` = 每秒 1 个请求

### 何时使用 `--respect-robots`
- **他人站点**：保持开启（默认：开启）
- **自有站点**（robots.txt 限制过多）：使用 `--no-robots`

### 问题优先级（高 → 低）

| 优先级 | 类型 | 分类 | 示例 |
|--------|------|------|------|
| 🔴 1 | error | SEO | 缺少标题标签 |
| 🔴 2 | error | Technical | 404、5xx 状态码 |
| 🔴 3 | error | Indexability | 重要页面被 noindex |
| 🟡 4 | warning | SEO | 标题过长或过短 |
| 🟡 5 | warning | Social | 缺少 OG/Twitter 标签 |
| 🟡 6 | warning | Technical | 缺少 canonical URL |
| 🔴 7 | error | Content | 图片损坏、缺少 alt 文本 |
| 🟡 8 | warning | Content | 内容过少（< 300 字） |
| 🟡 9 | warning | Performance | 页面加载慢（> 2 秒） |
| 🔵 10 | info | Technical | 检测到重定向（需验证） |

---

## JSON 输出结构

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
      "title": "页面标题",
      "meta_description": "描述内容...",
      "h1": "主标题",
      "h2": ["副标题"],
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
      "anchor_text": "关于我们",
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
      "issue": "缺少标题标签",
      "details": "该页面没有 title 标签"
    }
  ]
}
```

---

## 问题分类

### 问题类型

| 类型 | 含义 | 处理方式 |
|------|------|----------|
| `error` | 必须修复 | 缺少标题、404、noindex、图片损坏 |
| `warning` | 建议修复 | 标题过长/过短、内容单薄、页面慢 |
| `info` | 仅供参考 | 检测到重定向、信息性发现 |

### 问题分类

SEO · 技术 · 内容 · 移动端 · 可访问性 · 社交媒体 · 结构化数据 · 性能 · 可索引性 · 内容重复

---

## CLI 使用场景

| 场景 | 命令 |
|------|------|
| 快速审计 | `seocli https://example.com` |
| 静默模式（智能体） | `seocli https://example.com --quiet` |
| 保存到文件 | `seocli https://example.com --json report.json` |
| 本地开发 | `seocli http://localhost:3000 --delay 0` |
| 礼貌爬取 | `seocli https://other.com --delay 1.0 --respect-robots` |
| SPA 审计 | `seocli https://spa.com --js` |
| 深度爬取 | `seocli https://big.com --depth 5 --max-urls 2000` |
| 跳过重复检测 | `seocli https://big.com --no-duplicate-check` |

---

## 参数说明

```
seocli <url> [options]

positional:
  url                   要审计的网站 URL

options:
  --depth N             最大爬取深度（默认：3）
  --max-urls N          最大爬取 URL 数（默认：500）
  --delay SECONDS       请求间隔秒数（默认：0 = 无限制）
  --js                  启用 JavaScript 渲染（需要 playwright）
  --respect-robots      遵守 robots.txt（默认：开启）
  --no-robots           忽略 robots.txt
  --concurrency N       最大并发请求数（默认：5）
  --json FILE           将 JSON 输出保存到文件
  --quiet, -q           隐藏进度输出
  --no-duplicate-check  跳过内容重复检测（大型站点更快）
  --help                显示帮助信息
```

---

## 可选依赖

### JS 渲染

```bash
pip install seocli[js]
playwright install chromium
seocli https://spa-site.com --js
```

### MCP 模式

```bash
pip install seocli[mcp]
python -m seocli.server
```

---

## 许可证

MIT
