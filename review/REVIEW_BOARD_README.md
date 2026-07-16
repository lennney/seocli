# SEO Review Board

用AI模拟一个评审团队，帮你审方案。

[English](README_EN.md) | 中文

## 解决什么问题

你有一个方案（产品、技术、SEO内容策略...），想找不同角色的人帮你看看有没有问题。

传统做法：约会议、等人、开会、讨论、记录。耗时几天，成本高。

这个做法：让AI扮演PM、运营、技术、SEO、设计，各自独立看完，互相辩驳，给你一个带评分矩阵和解决方案的报告。几分钟搞定。

## 为什么不用普通的AI评审

直接问ChatGPT/Claude"帮我评审一下这个方案"，它倾向于同意你。

这个框架的做法：
1. **独立评审**：每个角色单独看，不互相参考
2. **辩驳机制**：角色们看完对方的意见后，会反驳、质疑、补充
3. **量化评分**：每个维度打1-5分，不是模糊的"还不错"
4. **必须出方案**：不能只批评，每个问题要给解决方案

就像真的开会一样——不同视角的人吵一架，比一个人自说自话靠谱。

## 特别擅长SEO内容策略评审

这是别的框架没有的。4个SEO专属角色：

| 角色 | 干嘛的 |
|------|--------|
| SEO策略师 | 关键词选择对不对？搜索量多少？竞争度？ |
| 内容质量审核 | 符合Google E-E-A-T吗？有没有内容农场风险？ |
| 技术SEO审核 | 页面速度、移动适配、结构化数据 |
| 竞品分析师 | 竞品怎么做的？流量多少？你和他们的差距？ |

还有Google政策合规检查——违反了就是5/5风险分，直接否决。

## 安装

### 一键安装

```bash
curl -sSL https://raw.githubusercontent.com/lennney/seo-review-board/master/install.sh | bash
```

装完后文件在 `~/.hermes/skills/seo/ai-team-review/`。

### Hermes

```bash
hermes skills install https://raw.githubusercontent.com/lennney/seo-review-board/master/SKILL.md
# 选 seo 分类
```

### Claude Code / Codex / 其他AI

```bash
# 克隆仓库
git clone https://github.com/lennney/seo-review-board.git

# 或者只复制核心文件
curl -sSL https://raw.githubusercontent.com/lennney/seo-review-board/master/SKILL.md -o SKILL.md
```

然后把 `SKILL.md` 的内容粘贴到对话开头，告诉AI"按照这个框架评审"。

## 使用

```
你：帮我评审一下这个SEO内容策略
AI：[派出4个SEO角色独立评审，汇总评分，辩驳，出解决方案]
```

就这么简单。不需要配置，不需要学API。

## 评审示例

gamixo.org 第一轮评审（真实数据）：

```
| 维度     | PM | 运营 | 技术 | SEO | 设计 | 平均 |
|----------|-----|------|------|-----|------|------|
| 可行性   | 3   | 4    | 2    | 5   | 3    | 3.4  |
| 成本     | 2   | 5    | 3    | 2   | 1    | 2.6  |
| 风险     | 4   | 3    | 4    | 5   | 2    | 3.6  |
```

SEO给了5/5风险分，原因是"RSS聚合+AI改写=内容农场，Google会惩罚"。

这个评审直接导致推翻原方案，重新找了"每日谜题游戏+攻略"的方向。跑了4轮迭代，评分从3.0涨到4.2。

这就是多角色评审的价值：单个视角看不到的盲点，多个视角能看到。

## 文件结构

```
├── SKILL.md                    # 核心方法论（8k字，10分钟读完）
├── install.sh                  # 一键安装脚本
├── adapters/
│   ├── hermes.md              # Hermes并行评审方式
│   ├── claude-code.md         # Claude Code适配
│   └── codex.md               # Codex适配
├── scenarios/
│   ├── product-review.md      # 产品评审模板
│   ├── seo-content-review.md  # SEO内容评审模板
│   └── tech-review.md         # 技术评审模板
├── roles/
│   └── library.md             # 12个角色定义
└── references/
    ├── scoring-system.md      # 评分体系（含SEO专属维度）
    ├── data-verification.md   # 数据验证方法
    └── ...（其他实战参考）
```

## 常见问题

**Q: 这和直接问AI"帮我评审"有什么区别？**

A: 直接问，AI倾向于同意你。这个框架让多个角色独立评审+辩驳，AI会真的挑战你。

**Q: AI扮演的角色靠谱吗？**

A: 不完美，但比没有强。关键是有具体的评分标准和验证机制，不是让AI自由发挥。

**Q: 我没有Hermes，能用吗？**

A: 能。SKILL.md是通用方法论，任何AI工具都能用。

**Q: 评审一次要多久？**

A: 简单方案5-10分钟，复杂方案30分钟（包括调研和辩驳）。

## License

MIT。随便用，随便改。

## 贡献

用了这个框架，有问题或者想法，提PR/Issue。

特别是：在实际项目中用了，把评审结果分享出来，让其他人看看真实效果。
