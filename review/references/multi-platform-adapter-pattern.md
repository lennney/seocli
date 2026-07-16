# 多平台适配模式（Adapters）

当一个 skill 需要在多个 AI 工具上运行时，使用 adapters/ 目录
为每个平台提供独立的适配文档。

## 目录结构

```
skill-name/
├── SKILL.md              # 核心方法论（通用，不绑定工具）
├── adapters/
│   ├── hermes.md         # Hermes适配
│   ├── claude-code.md    # Claude Code适配
│   └── codex.md          # Codex适配
└── ...
```

## SKILL.md 中的写法

在核心流程中用表格说明各平台的并行原语：

```markdown
| 工具 | 并行原语 | 配置 |
|------|---------|------|
| Hermes | `delegate_task(tasks=[...])` | `max_concurrent_children >= 角色数` |
| Claude Code | Task工具并行调用 | 无硬限制 |
| Codex | 并行task | 看配置 |
```

然后在 adapters/ 中详细说明每个平台的具体用法。

## Adapter 文件应包含

1. **并行机制**：该平台如何实现并行执行
2. **代码示例**：可直接复制使用的prompt/代码
3. **降级方案**：并行不可用时的替代方案
4. **注意事项**：该平台的限制和坑

## 各平台并行能力对比

| 平台 | 并行原语 | 隔离性 | 超时 | 适用场景 |
|------|---------|--------|------|---------|
| Hermes | delegate_task(tasks=[...]) | 完全隔离（独立上下文+终端） | 默认600s | 最适合多角色评审 |
| Claude Code | Task工具 | 部分隔离 | 无硬限制 | 适合并行任务 |
| Codex | 并行task | 看配置 | 看配置 | 代码相关任务 |

## 设计原则

1. **核心方法论与平台无关**：SKILL.md不应包含任何平台特定代码
2. **Adapter是可选的**：用户只看SKILL.md也能理解流程
3. **降级方案必须有**：如果某平台不支持并行，要有单线程替代方案
4. **示例要可复制**：每个adapter的代码示例应能直接使用
