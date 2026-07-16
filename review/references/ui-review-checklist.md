# UI/原型评审清单

> 用于HTML原型的多轮UI评审。评审人角色：UI设计师 + 移动端专家。

## 评审维度（8个）

### 1. 视觉层次
- 信息层级是否清晰？标题→描述→操作→元数据
- 重要元素是否突出？CTA按钮视觉权重够不够？
- Hero区域/首屏是否吸引注意力？

### 2. 色彩方案
- 配色是否协调？主色/辅色/中性色比例
- 对比度是否足够？（WCAG AA: 4.5:1文字，3:1大文字）
- 是否有品牌色彩变量？（Tailwind config中定义）
- 色盲友好？绿/黄/灰是否有替代标识（形状/图标）

### 3. 间距/排版
- 留白是否舒适？元素间呼吸空间
- 行高/字间距是否合理？
- 移动端间距是否需要调整？

### 4. 组件一致性
- 按钮圆角是否统一？（全部rounded-lg）
- Footer在所有页面是否一致？（py-8 text-sm）
- 按钮样式是否统一？（primary/secondary/ghost）
- 卡片组件是否统一？（padding/border/shadow）

### 5. 移动端适配（重点！）
- **触摸目标≥44px**（Apple HIG标准）
  - 键盘按键宽度
  - 模态框Close按钮
  - 面包屑链接
  - 小标签/徽章（如果是可点击的）
- **3档响应式断点**：
  - ≤380px（iPhone SE等超小屏）
  - ≤400px（一般小屏手机）
  - ≤640px（一般手机）
- 游戏操作区在小屏幕上是否可用？
- 键盘/网格总高度是否超出视口？（需要滚动才能操作=差）
- 横屏模式是否考虑？
- 汉堡菜单是否有展开逻辑？

### 6. 交互反馈
- hover状态（桌面端）
- active状态（所有按钮：`active:scale-[0.98] active:brightness-95`）
- focus-visible状态（键盘用户：`focus-visible:outline-2 outline-indigo-500`）
- transition是否只过渡必要属性？（`transform, box-shadow` 而非 `all`）
- 模态框：焦点陷阱、ESC关闭、点击遮罩关闭

### 7. 无障碍
- `<button>` vs `<div>` — 可交互元素必须用button
- aria-label — 所有图标按钮、导航按钮
- role属性 — grid/gridcell/row（游戏网格）、option（词卡）、dialog（模态框）
- aria-checked/aria-selected — 选中状态
- spoiler元素 — role="button" + tabindex="0" + aria-hidden
- Schema.org JSON-LD — 与页面可见内容一致

### 8. 游戏体验
- 胜利/失败弹窗是否完整？（emoji+标题+引导CTA）
- 当前行高亮（正在输入的行有视觉标识）
- 错误反馈动画（shake、toast替代alert）
- 分享功能（Web Share API优先，clipboard fallback）
- 动态文字更新（如"Submit (4 selected)"随选择变化）

## 典型高频问题

| 问题 | 频率 | 修复方式 |
|------|------|---------|
| 按钮圆角不统一 | 极高 | 全局搜索rounded→统一rounded-lg |
| 触摸目标<44px | 极高 | min-width/min-height: 44px |
| 缺少aria-label | 极高 | 批量给button/icon加 |
| div代替button | 高 | <div class→<button class |
| Footer不一致 | 高 | 统一py-8 text-sm |
| 汉堡菜单无功能 | 高 | 加mobile nav panel + toggle JS |
| 缺少active状态 | 高 | active:scale-[0.98] |
| 模态框无焦点陷阱 | 中 | 加onkeydown ESC监听 |
| transition: all | 中 | 改为transform, box-shadow |
| 拼写错误/HTML闭合 | 中 | 验证标签平衡 |

## 评审→修复→再评审循环

```
Round 1: 全面评审 → 输出问题清单（按严重度排序）
Round 2: 修复高优问题 → 再评审 → 验证修复 + 发现新问题
Round 3-5: 继续修复 → 直到P0/P1清零

每轮规则：
- 已修复且未回归的不重复报告
- 只报告新发现或修复不完整的问题
- 评分跟踪变化趋势
- UI评分用百分制或10分制（比产品评审的5分制更细）
```

## HTML原型规范（评审基准）

- `<script src="https://cdn.tailwindcss.com">` 加载样式
- Inter字体（Google Fonts CDN）
- 移动端优先响应式
- 示例数据填充（让页面看起来"真实"）
- 交互用JS实现基本行为
- Schema.org JSON-LD写在`<script type="application/ld+json">`
- 每个核心页面一个HTML文件
