# Hermes 适配

## 并行机制

使用 `delegate_task` 并行派出多个 subagent。

### 前置配置

```bash
# 角色数需 <= max_concurrent_children
hermes config set delegation.max_concurrent_children 6
hermes config set delegation.subagent_auto_approve true
```

### 单任务模式

```python
delegate_task(
    goal="你是产品经理。审核以下方案...",
    context="方案内容...",
    toolsets=["file", "web"]
)
```

### 批量并行模式（推荐）

```python
delegate_task(tasks=[
    {
        "goal": "你是产品经理。从需求合理性角度审核以下方案，给出风险评分(1-5)、核心质疑、建议。",
        "context": "方案内容...",
        "toolsets": ["file"]
    },
    {
        "goal": "你是运营总监。从运营执行角度审核以下方案...",
        "context": "方案内容...",
        "toolsets": ["file"]
    },
    {
        "goal": "你是SEO专家。从搜索优化角度审核以下方案...",
        "context": "方案内容...",
        "toolsets": ["file", "web"]
    }
])
```

### 结果汇总

subagent返回后，主agent汇总为评分矩阵：

```
| 维度 | PM | 运营 | SEO | 平均 |
|------|-----|------|-----|------|
| xxx  | 4/5 | 3/5  | 5/5 | 4.0  |
```

### 调研subagent

针对高风险问题，派出带web工具的调研subagent：

```python
delegate_task(
    goal="搜索'[关键词]'的行业数据和解决方案...",
    toolsets=["web", "search"]
)
```

### 注意事项

- subagent有超时限制（默认600秒，可通过 `delegation.max_iterations` 等配置调整）
- subagent没有当前对话上下文，所有信息通过context传递
- subagent可能编造数据，关键数字需主持人用terminal/browser验证
