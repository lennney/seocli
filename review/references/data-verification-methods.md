# 数据验证方法（调研 subagent 输出审查）

## 问题

Subagent 带 web/search 工具时，仍可能从训练知识编造数据而非实际搜索。
表现：报告格式规范、数字具体，但无来源 URL 或来源标注模糊（如"SEMrush"但无链接）。

## 验证策略（主持人必做）

### Level 1: 来源检查
- 每个数据点必须有 URL 或明确来源
- 无来源 → 标注 "⚠️ 未验证（训练知识）"

### Level 2: 直接验证（关键数据必做）
- 官方页面：curl 目标网站的 about 页面、Schema.org JSON-LD
- 公开 API：curl 可访问的公开数据端点
- Wikipedia：curl 对应页面提取 infobox 数据

### Level 3: 交叉验证
- 同一数据从 2 个独立来源确认
- 数量级判断：即使具体数字不准，趋势方向是否一致

## 验证模板（terminal 命令）

```bash
# 抓官方 about 页面的 Schema.org 数据
curl -sL "https://about.example.com/" | grep -o '"@type":"Organization"[^}]*}'

# 抓 Wikipedia infobox
curl -sL "https://en.wikipedia.org/wiki/Topic" | grep -i "million\|billion\|users\|traffic"

# 抓公开 SEO 数据（如果可访问）
curl -sL "https://trends.google.com/trends/api/widgetdata/..." 
```

## 可信度标注规范

| 标注 | 含义 | 后续动作 |
|------|------|---------|
| ✅ 已验证 | 直接从官方/可访问源确认 | 可直接使用 |
| ⚠️ 可能对 | 有间接证据支持但未直接验证 | 使用时注明不确定性 |
| ❌ 未验证 | 仅来自模型训练知识 | 不可直接使用，需验证或删除 |
