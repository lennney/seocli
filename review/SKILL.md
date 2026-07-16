---
name: ai-team-review
description: "Use when reviewing product proposals, technical designs, SEO content strategies, or any decision needing multiple expert perspectives. Multi-agent cross-functional review with SEO-specific roles (E-E-A-T, Google policy, keyword strategy). Independent scoring → debate → solutions → action plan."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [review, multi-agent, product, seo, evaluation, cross-functional]
    related_skills: [writing-plans, requesting-code-review, claude-code, codex]
---

# AI 跨职能团队评审框架

多Agent模拟跨职能团队（PM/运营/技术/SEO/设计），对方案进行独立评审→辩驳→出解决方案→生成行动计划。

**实战验证**：本框架基于gamixo每日谜题项目4轮迭代评审实践（3.0→3.6→3.9→4.2分），覆盖产品方向探索、SEO内容策略、UI原型评审等场景。

## When to Use

- 新产品/新功能方案评审
- 技术架构方案评审
- SEO内容策略评审
- 商业模式可行性分析
- 需求文档评审
- 代码/PR评审（需多视角）

**Don't use for:** 简单yes/no决策、纯执行任务、不需要多视角的小改动。

## Quick Start

```
用户：帮我评审一下这个产品方案

1. 读取方案文档
2. 选择角色组合（见下方场景表）
3. 并行派出subagent独立评审
4. 汇总评分矩阵
5. 针对高风险问题调研+辩驳
6. 生成最终报告+行动计划
```

## 核心流程（4阶段制）

> 注意：核心流程的"Phase"是评审阶段，与下方"迭代节奏"的"Round"（迭代轮次）不同。
> 一次评审可能经历多轮迭代（Phase 1评审→发现问题→修复→Round 2再评审→...）。

### Phase 1: 独立评审

角色之间不交流，确保独立性。每个角色按维度打分（1-5风险分）+ 核心质疑 + 建议。

**并行执行方式（按工具选择）：**

| 工具 | 并行原语 | 配置 |
|------|---------|------|
| Hermes | `delegate_task(tasks=[...])` | `delegation.max_concurrent_children >= 角色数` |
| Claude Code | Task工具并行调用 | 无硬限制 |
| Codex | 并行task | 看配置 |

**评分格式（每个角色输出）：**

```
| 维度 | 风险评分(1-5) | 核心质疑 | 建议 |
|------|--------------|---------|------|
| xxx  | 4/5 🟠       | 一句话  | 一句话 |
```

### Phase 2: 辩驳 & 解决方案

1. 主持人整理 Round 1 的争议点
2. 针对每个 P0/P1 问题，上网调研解决方案
3. 角色读取他人评审后反驳、补充、修正
4. 达成共识后出具体解决方案

**解决方案格式：**
```
问题：[一句话]
解决方案：[具体步骤]
成本：[估算]
时间：[估算]
成功标准：[怎么算完成]
```

### Phase 3: 行动计划

按优先级排序（P0 > P1 > P2），每个行动项包含：负责人/时间/成本/成功标准。

### Phase 4: 产品文档（评审通过后）

产出顺序（用户确认一个再做下一个）：
1. PRD → 2. IA → 3. HTML原型 → 4. 用户故事 → 5. Sprint排期

## 角色组合速查

| 场景 | 推荐角色 |
|------|---------|
| 产品方案评审 | PM + 运营 + 技术 + SEO + 设计 |
| 技术方案评审 | 架构师 + 后端 + 前端 + DevOps + 安全 |
| SEO内容评审 | SEO策略师 + 内容质量 + 技术SEO + 竞品分析 |
| 需求评审 | PM + 技术 + 测试 + 运营 |
| 商业模式评审 | PM + 运营 + 财务 + 市场 |

## 角色库

### 产品类

| 角色 | 视角 | Prompt前缀 |
|------|------|-----------|
| 产品经理 | 需求合理性、用户价值 | `你是产品经理。从需求合理性角度提出尖锐质疑。` |
| 运营总监 | 运营可行性、成本 | `你是运营总监。从运营执行角度提出尖锐质疑。` |
| SEO专家 | 搜索排名、内容农场风险 | `你是SEO专家。从搜索优化角度提出尖锐质疑。` |

### 技术类

| 角色 | 视角 | Prompt前缀 |
|------|------|-----------|
| 技术负责人 | 架构、技术选型 | `你是技术负责人。从技术实现角度提出尖锐质疑。` |
| 前端工程师 | UX、性能、可访问性 | `你是前端工程师。从用户体验角度提出质疑。` |
| DevOps | 部署、运维、成本 | `你是DevOps工程师。从部署运维角度提出质疑。` |

### SEO专属（新增）

| 角色 | 视角 | 关注点 |
|------|------|--------|
| SEO策略师 | 关键词、搜索意图 | 搜索量、竞争度、长尾机会、意图匹配 |
| 内容质量审核 | E-E-A-T、原创度 | Google HCU政策、内容农场风险、AI内容合规 |
| 技术SEO审核 | 爬虫、索引 | Core Web Vitals、结构化数据、移动适配 |
| 竞品分析师 | 市场格局 | 流量来源、内容差距、外链策略 |

### 其他

| 角色 | 视角 | Prompt前缀 |
|------|------|-----------|
| 设计师 | UX、信息架构 | `你是设计师。从用户体验角度提出质疑。` |
| 财务 | 成本、ROI | `你是财务。从成本和投资回报角度提出质疑。` |
| 测试工程师 | 质量、边界case | `你是测试工程师。从质量保障角度提出质疑。` |

## 评分标准

### 风险评分（1-5）

- **5/5 🔴** 致命问题，不解决不应启动
- **4/5 🟠** 严重问题，上线前必须解决
- **3/5 🟡** 中等风险，有workaround
- **2/5 🟢** 小问题，不影响大局
- **1/5 ⚪** 无风险

### 整体可行性

- **4-5/5**：成熟，可执行
- **3-4/5**：基本可行，需调整
- **2-3/5**：问题较多，需重大修改
- **1-2/5**：不可行，需重新设计

## 数据验证（主持人必做）

Subagent可能编造数据。验证策略：

1. **来源检查**：每个数据点必须有URL，无来源标"⚠️未验证"
2. **直接验证**：关键数据用curl抓官方页面确认
3. **交叉验证**：同一数据从2个独立来源确认

## 迭代节奏

```
Round 1: 独立评审 → 评分矩阵 → 问题清单
Round 2: 修复问题 → 再评审 → 验证修复
Round 3: 继续修复 → 再评审 → 聚焦剩余
Round N: 直到无阻塞问题 → 进入开发
```

每轮规则：已修复的问题不重复报告，只报告新发现或修复不完整的问题。

## Common Pitfalls

1. **角色互相通气**：Round 1必须独立，否则群体思维
2. **评分不具体**：每个分数必须有理由
3. **只批评不出方案**：Round 2必须针对每个P0/P1出解决方案
4. **编造数据**：调研结果必须标注来源，关键数字要二次验证
5. **回避争议**：争议点最有价值，要充分辩论
6. **行动项无成功标准**：每个action都要有"怎么算完成"
7. **subagent写大文档超时**：拆小任务或主agent直接写
8. **文档间不一致**：修复时用search_files全局搜索确保同步

## 输出文件规范

```
{project}/
├── XX-team-review-round1.md    # 独立评审
├── XX-team-review-round2.md    # 辩驳+解决方案
└── XX-team-review-final.md     # 最终报告+行动计划
```

## Verification Checklist

- [ ] 角色组合是否覆盖所有关键视角
- [ ] Round 1每个角色是否独立评审（无交叉）
- [ ] 评分是否有具体理由
- [ ] P0/P1问题是否有具体解决方案
- [ ] 行动项是否有成功标准
- [ ] 关键数据是否经过验证
- [ ] 输出文件是否命名规范

## 参考文件

### 核心流程
- `adapters/hermes.md` — Hermes适配详解
- `adapters/claude-code.md` — Claude Code适配
- `adapters/codex.md` — Codex适配

### 场景模板
- `scenarios/product-review.md` — 产品评审场景模板
- `scenarios/seo-content-review.md` — SEO内容评审模板
- `scenarios/tech-review.md` — 技术评审模板

### 角色与评分
- `roles/library.md` — 完整角色库（含Prompt模板）
- `references/scoring-system.md` — 评分体系详解（含SEO专属维度）

### 实战参考（来自gamixo项目）
- `references/iterative-review-pattern.md` — 迭代评审模式（方向探索→验证→再评审）
- `references/document-review-iteration.md` — 文档评审迭代模式（评审→修复→再评审循环）
- `references/document-consistency-checklist.md` — 文档间一致性检查清单
- `references/data-verification-methods.md` — 数据验证方法（3级验证策略）

### 交付物模板
- `references/prd-template.md` — PRD模板
- `references/product-doc-checklist.md` — 产品文档完整清单
- `references/html-prototyping-pattern.md` — HTML原型制作模式
- `references/ui-review-checklist.md` — UI/原型评审清单

### Skill工程
- `references/skill-audit-pattern.md` — Skill审核模式（subagent作为skill工程师审核）
- `references/multi-platform-adapter-pattern.md` — 多平台适配模式（adapters/结构）
