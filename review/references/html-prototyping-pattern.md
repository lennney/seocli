# HTML 原型制作模式

## 适用场景

评审通过后，需要给用户和开发团队展示"产品长什么样"。
比静态线框图更直观，比Figma更快，开发团队可以直接参考代码。

## 技术栈

- Tailwind CSS（CDN加载，零构建）
- Inter 字体（Google Fonts CDN）
- 原生JS（交互行为）
- 响应式设计（移动端优先）

## 文件模板

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{页面标题}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    body { font-family: 'Inter', sans-serif; }
  </style>
</head>
<body class="bg-gray-50 min-h-screen">
  <!-- Header -->
  <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
      <a href="/" class="flex items-center gap-2">
        <span class="text-2xl">🎯</span>
        <span class="font-bold text-lg">{品牌名}</span>
      </a>
      <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
        <a href="#">Nav1</a>
        <a href="#">Nav2</a>
      </nav>
      <button class="md:hidden text-gray-600">☰</button>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-5xl mx-auto px-4 py-8">
    <!-- 内容区域 -->
  </main>

  <!-- Footer -->
  <footer class="bg-white border-t border-gray-200 py-6">
    <div class="max-w-5xl mx-auto px-4 text-center text-xs text-gray-400">
      © 2026 {品牌名}
    </div>
  </footer>
</body>
</html>
```

## 预览方法

1. 如果Playwright未安装：`npx playwright install chromium`
2. 用 `browser_navigate` 打开本地文件：`file:///path/to/prototype/01-page.html`
3. 用 `browser_vision` 截图给用户预览

```
terminal: npx playwright install chromium
browser_navigate(url="file:///path/to/prototype/01-page.html")
browser_vision(question="What does this page look like?")
```

## 设计规范

### 颜色系统
- 主色：indigo-600（按钮、链接）
- 成功：green-100/700（badge、状态）
- 警告：amber-500（提示、CTA）
- 错误：red-600（危险操作）
- 中性：gray-50/100/200/400/600/900

### 组件模式
- 卡片：`bg-white rounded-xl shadow-sm border border-gray-200`
- 按钮主：`bg-indigo-600 text-white font-semibold py-2 rounded-lg hover:bg-indigo-700`
- 按钮次：`bg-gray-100 text-gray-700 font-semibold py-2 rounded-lg hover:bg-gray-200`
- Badge：`bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded-full`
- 折叠面板：`<details class="bg-white rounded-lg border border-gray-200">`

### 间距
- 页面最大宽度：`max-w-5xl`（内容页）或 `max-w-3xl`（文章页）
- 区块间距：`mt-8` 或 `mt-10`
- 卡片内边距：`p-5` 或 `p-4`

### SEO相关原型
- 攻略/内容页需要包含 Schema.org JSON-LD
- 用 `<script type="application/ld+json">` 写在 body 底部
- 包含 FAQ 折叠面板（用 `<details>` 实现）
- 答案/剧透区域用点击揭示（JS toggle class）

## 原型评审常见问题（gamixo 3轮评审实测）

### 必须避免的问题
1. **品牌名引用错误**：原型中引用了其他品牌名（如"WORDLE"）→ 改为自研名称
2. **语言混入**：目标语言是英文但原型中混入中文 → 全文检查
3. **MVP功能遗漏**：砍掉的功能在原型中未移除 → 移除或标注Phase 2
4. **答案/数据不一致**：多个原型中同一Puzzle的答案不同 → 统一
5. **重复ID**：HTML中id属性重复 → 修复

### 推荐加入的交互
1. **胜利/失败弹窗**：游戏完成后的状态反馈+下一步引导
2. **答案二次确认**：剧透内容需要confirm()确认
3. **渐进提示级联**：Hint 2显示后才出现Hint 3按钮
4. **移动端响应式**：@media查询缩小方块/键盘尺寸
5. **锚点导航**：长页面增加Jump to导航
6. **内嵌游戏iframe**：攻略页内嵌可玩游戏（sandbox安全策略）
7. **localStorage状态**：游戏完成状态、Streak数据

### iframe嵌入游戏的CSS模式
```css
.game-iframe-wrap {
  position: relative; padding-bottom: 80%; height: 0;
  overflow: hidden; border-radius: 12px; border: 2px solid #e5e7eb;
}
.game-iframe-wrap iframe {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;
}
```
sandbox属性：`sandbox="allow-scripts allow-same-origin"`

### 剧透/答案区的交互模式
```javascript
// 点击揭示（简单版）
onclick="this.querySelector('.spoiler').classList.toggle('revealed')"

// 二次确认版（推荐）
onclick="if(confirm('确定要看？这会剧透！'))this.querySelector('.spoiler').classList.toggle('revealed')"
```

### 游戏胜利/失败弹窗模式
```html
<!-- 胜利弹窗（hidden by default） -->
<div id="winModal" class="hidden fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div class="bg-white rounded-2xl p-8 max-w-sm mx-4 text-center">
    <p class="text-5xl mb-3">🎉</p>
    <h2 class="text-2xl font-bold">You Got It!</h2>
    <p class="text-gray-500 mt-2">Solved in X/6 attempts</p>
    <div class="flex gap-3 mt-6">
      <button onclick="shareResult()" class="flex-1 bg-gray-900 text-white py-2 rounded-lg">Share</button>
      <a href="/next-game/" class="flex-1 bg-indigo-600 text-white py-2 rounded-lg text-center">Next Game</a>
    </div>
  </div>
</div>
```

## 文件组织
```
docs/{project}/prototype/
├── 01-homepage.html      首页
├── 02-{core-page}.html   核心功能页
├── 03-{content-page}.html 内容页
└── ...
```
