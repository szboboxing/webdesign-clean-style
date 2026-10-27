# 简洁风格美化 · 设计指南

一套骨架、两张皮肤。骨架（结构件 + 排版规则）在 `assets/components.css`，皮肤（颜色 token）在
`assets/theme-light.css`（明亮清新）与 `assets/theme-dark.css`（暗黑忧郁）。
换皮肤只改 token，不动结构；改结构只动 components，两套皮肤同时生效。

## 1. 设计语言总纲

- **暖纸编辑风骨架**：纸感底色 + 两团模糊色晕做 Hero，不用硬边框，靠柔和阴影和发丝线分层。
- **大圆角**：卡片 22px、表格容器 16px、代码块 18px、Hero 28px（600px 以下收到 22px）。
- **章节徽章**：「一二三四」做成 36px 圆角方块，主色浅底 + 主色字；`{alt}` 章节换次色。
- **吸顶药丸导航 + 3px 渐变进度条**：取代常驻侧边目录，窄屏导航横向滑动。
- **目录卡**：默认 4 张，悬浮抬起 7px，960px 两列、600px 一列。
- **表格无边框**：表头浅底小字（11.8px，字距 .05em），行间发丝线，悬浮整行微染主色。
- **自定义列表符**：无序 6px 小圆点，有序 21px 浅底数字圆。
- **分隔线**是居中的 `· · ·`，不是横线。
- **明/暗双主题**：跟随系统 + 手动切换 + localStorage 记忆；回到顶部；打印样式。
- **配色按语义分工**：主色（青绿 / 雾蓝）给流程与正文强调，次色（陶土 / 暗紫）给附录、提示块与警告。

## 2. Token 表

| token | 明亮清新 | 暗黑忧郁 | 用途 |
|---|---|---|---|
| `--bg` | `#FFFCF6` | `#101318` | 页面底 |
| `--paper` | `#FFFFFF` | `#171B21` | 卡片、表格、代码块外的面板 |
| `--paper2` | `#FAF3E9` | `#1E232B` | 表头、chip 等次级底 |
| `--ink` | `#241F1A` | `#E4E8F0` | 标题字 |
| `--ink2` | `#4C453D` | `#B7BECA` | 正文字 |
| `--muted` | `#6E6558` | `#8E97A6` | 小字、说明、表头字 |
| `--hair` | `rgba(36,31,26,.10)` | `rgba(228,232,240,.10)` | 发丝线 |
| `--rim` | `rgba(36,31,26,.04)` | `rgba(255,255,255,.06)` | 卡片顶部 1px 高光边（暗色主题靠它不"沉底"） |
| `--accent` | `#17A398` 青绿 | `#7FA8C9` 雾蓝 | 图形用主色：圆点、徽章底、进度条、色晕 |
| `--accent-ink` | `#0E7C73` | `#9CC3E0` | 文字用主色：链接、卡片标题、选中态底 |
| `--accent2` / `--accent2-ink` | `#D2705F` / `#B4523F` | `#A98BB0` / `#C0A5C6` | 次色，同上两种用途 |
| `--on-accent` / `--on-accent2` | `#FFFFFF` | `#101318` | 压在点色上的反色字（暗色主题必须是深字，不能是白字） |
| `--sh` / `--shh` | 暖棕调柔影 | 纯黑深影 | 常态 / 悬浮态 |
| `--nav` | `rgba(255,252,246,.84)` | `rgba(16,19,24,.82)` | 吸顶导航毛玻璃底 |
| `--herobg` | 白→暖米渐变 | 石墨蓝渐变 | Hero 面板底 |
| `--glow-a` / `--glow-b` | `.34` / `.26` | `.20` / `.16` | 两团色晕不透明度（暗色要压更低，否则发灰） |
| `--codebg`/`--codeink`/`--codecap`/`--codebtn`/`--codehair` | 米白底 + 深墨字 | 近黑底 + 冷白字 | 代码块五件套 |
| `--vignette` | 未定义（回落 `none`） | 顶部微光 + 底部压暗 | 暗色主题的氛围层，`body::before` 固定覆盖 |

> 新增皮肤＝复制一份 token 文件、改颜色、在 `build_page.py` 的 `read_assets()` 列表里加一行。

## 3. 结构件规格

| 结构件 | 关键规格 |
|---|---|
| `.progress` | `position:fixed;top:0;height:3px`，内层 `i` 宽度由 JS 写百分比，`linear-gradient(90deg,accent,accent2)` |
| `nav.pills` | `sticky;top:3px`（让开进度条），`overflow-x:auto` + 隐藏滚动条，`backdrop-filter:blur(16px) saturate(1.4)` |
| `.hero` | `overflow:hidden` 必须留着，否则两团色晕会溢出造成横向滚动；`::before/::after` 是 460/400px 圆 + `blur(70px)` |
| `.cards` / `.card` | grid 4 列，`translateY(-7px)` 悬浮；卡内 `.n` 序号、`.t` 标题、`.d` 说明 |
| `.tw` / `table` | 外层 `overflow-x:auto` + 16px 圆角；表格 `border-collapse:separate`、`min-width:470px`（600px 以下 430px）；行线用 `td{border-top}`，首行去掉 |
| `ul/ol li::before` | 无序圆点 `left:8px;top:.63em`；有序数字圆 `counter(c)`，`li{padding-left:28px}` 给它让位 |
| `.note` | `>` 引用渲染成次色浅底提示块，18px 圆角 |
| `.dotrule` | `---` 渲染成居中 `· · ·`，`letter-spacing:.55em` |
| `figure.code` | `figcaption` 左文件名右复制按钮，`pre{overflow-x:auto}`，`code{white-space:pre}` 不折行 |
| `#top` | 46px 圆钮，`opacity:0` + `translateY(14px)`，滚动过 480px 加 `.show` |

## 4. 响应式与无障碍

- 断点只有两个：`960px`（卡片 4→2 列）、`600px`（卡片 1 列、Hero 圆角与色晕缩小、表格字号 13px、导航药丸缩小）。
- **页面本身永远不横向滚动**：宽表格和长代码行都在自己的 `overflow-x:auto` 容器里消化。
  验收方法：浏览器里比 `document.documentElement.scrollWidth` 与 `clientWidth`，必须相等。
- 对比度门槛：正文与小字 ≥ 4.5，大字/图形 ≥ 3.0。`scripts/check_page.py` 会逐对算并判 FAIL。
- `prefers-reduced-motion` 关掉全部过渡与平滑滚动。
- 打印：隐藏导航/进度条/回顶/复制按钮/氛围层，去阴影，代码块改浅底并允许折行，`.sec`/`table`/`figure`/`li` 不跨页断开。
- `<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">` 必带；
  `color-scheme` 随主题切（`:root{color-scheme:light}` / `html[data-theme=dark]{color-scheme:dark}`），滚动条和表单控件才跟着变色。

## 5. 交互规格

- **三态主题按钮**：浅色 → 深色 → 跟随系统 → 浅色。非默认态给按钮加 `.act`（次色底）作视觉提示。
- **记忆**：`localStorage` 存 `dark` 或 `auto`；选回浅色（默认态）时 `removeItem` 清键，别留脏值。
  存了 `auto` 时首屏内联脚本会去问系统，这是用户显式选过的，允许跟随系统变暗。
- **防闪白**：`<head>` 里放一段内联脚本先上色，别等主脚本。默认浅色时判断写成
  `(m==='dark')||(m==='auto'&&matchMedia(dark).matches)`——**不要**让系统深色直接盖掉浅色默认。
- **进度条**：`(scrollTop)/(scrollHeight-clientHeight)*100`，`scroll` 与 `resize` 都挂，`passive:true`。
- **当前章节高亮**：单个 `IntersectionObserver`，`rootMargin:"-14% 0px -70% 0px"`，取相交里 top 最小的那个。
- **复制按钮**：优先 `navigator.clipboard.writeText`，失败回落 `execCommand("copy")`（file:// 下常需要回落），
  成功文案 1.5 秒后还原。

## 6. 制作流程

1. 读源 Markdown，确认它只用到受支持的子集（见 `build_page.py` 文档串）。有别的语法先说明会退化成纯文本。
2. **问用户要哪套皮肤**：明亮清新 / 暗黑忧郁 / 两套都要（默认单文件双主题，`--theme` 只决定首屏）。
3. 在源文件顶部补指令注释（`hero-title`、`hero-kicker`、`hero-lede`、`chips`、`cards`、`foot`）；
   章节多时给 `## ` 标题加 `{pill:短标签}`，附录类章节加 `{alt}`。不补也能跑，会自动取前 4 章做卡片。
4. 构建：`python scripts/build_page.py 源.md -o 产物.html --theme light|dark`；
   要贴进对话就加 `--fragment`（不带 `<html>`，交给宿主渲染）。
5. 自检：`python scripts/check_page.py 源.md 产物.html`，必须 `RESULT: PASS`；FAIL 就改 token 再跑，不要放行。
6. 浏览器实测（能开就开）：读计算样式确认首屏主题、`scrollWidth` 无溢出、点主题按钮走完三态、
   点药丸跳转、点复制、滚动看进度条与回顶。
7. 交付：报产物路径 + 实测结论。**截图不可用就如实说**——计算样式能证明配色和布局，证明不了观感。
8. 改内容只改源 md，重跑第 4-5 步；不要手改产物 HTML。

## 7. 坑（都踩过）

- **暗色主题里白字压浅点色**：`#9CC3E0` 上写白字只有 1.86。凡是"点色底 + 反色字"的地方一律用 `--on-accent`，
  暗色主题给深字。
- **浅色主题的链接色**：`#17A398` 直接当链接色在暖白底上只有 3.05。图形用 `--accent`、文字用 `--accent-ink`，两个 token 分开。
- **小字灰度**：`#857C70` 在白卡上 4.11、表头 3.73，都不达标；加深到 `#6E6558` 后 5.73 / 5.20。
- **浅色主题的代码块别用整块黑底**：大面积深色板块会让整页"显暗"，浅色主题下代码块用米白底 + 深墨字。
- **`transition` 会让读回的样式骗人**：body 有 `background .35s ease` 时，切主题后立刻读 `backgroundColor`
  拿到的是过渡中间值（甚至旧值）。要验 token 是否生效，读
  `getComputedStyle(document.documentElement).getPropertyValue('--bg')`，别读 body 的背景色。
- **隐藏页面里 scroll / IntersectionObserver 不推进**：无头或被隐藏的浏览器里程序化 `scrollTo` 可能不派发滚动事件，
  进度条读到 0%。手动 `dispatchEvent(new Event('scroll'))` 再读，才能区分"没生效"和"没被触发"。
- **列表首项最容易丢**：md 列表解析要先用第一行播种 `items`，再进循环，否则每个列表少一条。
- **表格宽度**：给 `table` 设 `min-width` 时必须同时保证外层容器 `overflow-x:auto`，否则窄屏整页横向滚动。
- **色晕溢出**：`.hero` 少了 `overflow:hidden`，两团 blur 圆会撑出横向滚动条。
- **Windows 控制台 cp936**：脚本打印中文会乱码。脚本内 `sys.stdout.reconfigure(encoding='utf-8')`，
  或把结果写文件再读。
- **`## 附录 A —— xxx` 这类标题**要单独处理徽章和短标签，否则药丸导航里会出现"脚本 A —— 附录 xxx"这种垃圾文案。
