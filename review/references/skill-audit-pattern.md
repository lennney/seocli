# Skill 审核模式（Subagent as Skill Engineer）

用 delegate_task 派出一个 subagent 作为"Skill 工程师"审核 skill 质量。
适用于：skill 大改后、发布前、多人协作场景。

## 何时使用

- Skill 创建或重大重构后
- 准备分发给他人使用前
- 迭代多轮后检查一致性

## 审核维度模板

```
1. Frontmatter合规
   - name ≤64 chars, 小写+连字符
   - description 以"Use when..."开头, ≤1024 chars
   - version/author/license/metadata.hermes.{tags,related_skills} 必须存在

2. 结构规范
   - Overview → When to Use → 主体 → Common Pitfalls → Verification Checklist
   - 主文件目标 8-15k chars

3. 内容质量
   - 触发条件是否清晰（正面+反面）
   - 步骤是否可执行
   - Pitfalls是否具体（非泛泛而谈）
   - 参考文件是否完整

4. 多平台适配（如适用）
   - 各平台adapter是否覆盖
   - 并行机制是否准确
   - 是否考虑平台限制

5. 实战验证
   - 是否有真实案例
   - Pitfalls是否来自实战
   - 评分标准是否经过检验
```

## 审核Prompt模板

```
你是一名Skill工程师，负责审核Hermes Agent skill的质量。

请读取以下文件并审核：
- {skill_dir}/SKILL.md
- {skill_dir}/references/*.md
- {skill_dir}/adapters/*.md（如存在）
- {skill_dir}/scenarios/*.md（如存在）

审核标准：{见上方维度}

输出格式：
## 总体评分：X/10
## 审核维度（每个维度：评分+问题+建议）
## 关键问题（必须修复）
## 改进建议（可选优化）
## 亮点
```

## 实战案例：ai-team-review 审核

**审核结果：7.5/10**

发现的关键问题：
1. 5个reference文件未在SKILL.md参考文件列表中 → 补充
2. "Round"命名冲突（核心流程 vs 迭代节奏）→ 改为Phase/Round区分
3. FID指标已过时 → 更新为INP

发现的亮点：
- SEO评审能力突出（4专属角色+量化标准+政策红线）
- 实战验证充分（gamixo项目4轮迭代）
- 数据验证意识强（3级验证策略）

## 注意事项

- 审核subagent应使用file/terminal工具集（不需要web）
- 审核报告应直接输出，不要写入文件（由主持人决定是否采纳）
- 审核subagent可能误判（如标记存在文件为缺失），主持人需二次确认
- 建议在skill重构后立即审核，不要等到发布前
