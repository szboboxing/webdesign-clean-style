# webdesign · 网页简洁风格美化 202610 v1.1

一个 Qoder Skill：把 Markdown 文档渲染成**单文件、零依赖、可直接双击打开**的美化 HTML 页面。
一套骨架、两张皮肤，手机 / 平板 / 电脑三端自适应，明暗主题可切换并记忆。

## 两套皮肤

| | 明亮清新版 | 暗黑忧郁版 |
|---|---|---|
| 气质 | 暖纸、白纸卡、清透 | 深夜书房、石墨蓝、雾面低饱和 |
| 页面底 | `#FFFCF6` | `#101318` |
| 主点色 | 青绿 `#17A398`（文字用 `#0E7C73`） | 雾蓝 `#7FA8C9`（文字用 `#9CC3E0`） |
| 次点色 | 陶土 `#D2705F`（文字用 `#B4523F`） | 暗紫 `#A98BB0`（文字用 `#C0A5C6`） |
| 氛围 | Hero 两团模糊色晕 | 色晕压暗 + 顶部微光 + 底部暗角 |
| 适合 | 白天、打印、汇报 | 夜间、长文阅读 |

两套皮肤同时打进同一个 HTML，右上角按钮三态切换：**浅色 → 深色 → 跟随系统**，选择存 `localStorage`。
`--theme` 只决定首屏先显示哪一套；不带参数时首屏是明亮清新版，系统深色不会自动盖掉它。

## 设计语言

- 暖纸编辑风骨架：纸感底 + Hero 双色晕，不用硬边框，靠柔和阴影与发丝线分层
- 大圆角：卡片 22px / 表格容器 16px / 代码块 18px / Hero 28px
- 吸顶药丸导航（窄屏横滑）+ 顶部 3px 渐变阅读进度条，取代常驻侧边目录
- 4 张可悬浮抬起的目录卡，960px 两列、600px 一列
- 表格无边框：表头浅底小字、行间发丝线、悬浮整行微染
- 自定义列表符：无序小圆点、有序浅底数字圆；分隔线是居中的 `· · ·`
- 代码块带标题栏与复制按钮（`navigator.clipboard` + `execCommand` 双路径）
- 回到顶部浮动按钮、打印样式、`prefers-reduced-motion` 支持
- 对比度按 WCAG 卡线：小字 ≥ 4.5，大字/图形 ≥ 3.0，脚本自动校验

完整规格见 [`references/design-guide.md`](references/design-guide.md)。

## 安装

把本目录整体拷进 Qoder 的用户级 skill 目录，重启会话或执行 `/skills reload`：

```sh
# Windows
xcopy /E /I "webdesign-网页简洁风格美化-202610v1.1" "%USERPROFILE%\.qoder-cn\skills\webdesign-网页简洁风格美化-202610v1.1"

# macOS / Linux
cp -R "webdesign-网页简洁风格美化-202610v1.1" ~/.qoder-cn/skills/
```

之后对话里说「美化这个页面」「把 md 做成好看的 HTML」「做个明亮版/暗色版」即可触发，
也可以直接 `/webdesign-网页简洁风格美化-202610v1.1`。

> skill 名称含中文与点号，实测可被 Qoder 正常加载并出现在可用列表中。

## 直接用脚本（不装 skill 也能跑）

只需要 Python 3，无第三方依赖：

```sh
# 明亮清新版首屏
python scripts/build_page.py example/demo.md -o demo-light.html --theme light

# 暗黑忧郁版首屏
python scripts/build_page.py example/demo.md -o demo-dark.html --theme dark

# 贴进聊天窗口的片段（不含 <html>）
python scripts/build_page.py example/demo.md -o frag.html --fragment

# 交付前自检：标签配平 / 内容零丢失 / 双主题对比度 / 12 项功能件
python scripts/check_page.py example/demo.md demo-light.html
```

`example/demo-light.html` 与 `example/demo-dark.html` 是用 `example/demo.md` 生成的成品，
可直接双击打开对比两套皮肤。

### 源文件指令（都可选）

```md
<!-- hero-title: 页面主标题 -->
<!-- hero-kicker: 标题上方的小字 -->
<!-- hero-lede: 一句话导语 -->
<!-- chips: 标签一 | 标签二 -->
<!-- cards: 01|卡片标题|一句话说明|#s2|a -->
<!-- foot: 页脚一行字 -->

## 3. 检验过程 {pill:验收}
## 附录 A —— 脚本原文 {alt}
```

支持的 Markdown 子集：`#`/`##`/`###`、`|表格|`、``` 代码块、`-` 与 `1.` 列表（可带缩进续行）、
`>` 引用、`---` 分隔线、`**粗体**`、`` `行内码` ``、`[文字](链接)`。

## 目录

```
webdesign-网页简洁风格美化-202610v1.1/
├── SKILL.md                    # skill 主文件：触发条件、皮肤选择、工作流、硬性约束
├── scripts/
│   ├── build_page.py           # md -> 单文件 HTML（双主题 + 全部结构件）
│   └── check_page.py           # 无浏览器自检，FAIL 时退出码 1
├── assets/
│   ├── theme-light.css         # 明亮清新版 token
│   ├── theme-dark.css          # 暗黑忧郁版 token（含暗角氛围层）
│   └── components.css          # 共用结构件 + 响应式 + 打印
├── references/
│   └── design-guide.md         # 设计语言、token 表、结构件规格、流程、坑清单
└── example/
    ├── demo.md                 # 覆盖全部结构件的样例源文件
    ├── demo-light.html         # 成品：明亮清新首屏
    └── demo-dark.html          # 成品：暗黑忧郁首屏
```

## 加第三套皮肤

1. 复制 `assets/theme-light.css` 改名（如 `theme-sepia.css`），只改 token 值
2. 在 `scripts/build_page.py` 的 `read_assets()` 文件名列表里加一行
3. 在 `scripts/check_page.py` 的 `themes` 字典里登记，让它也进对比度校验
4. 重跑 build + check，`RESULT: PASS` 才算完成

## 许可

MIT
