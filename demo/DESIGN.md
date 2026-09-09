# DESIGN.md

> 一份安静的阅读工具，标题是唯一的主角，其余一切退到背景里。

## 1. Visual Theme & Atmosphere

**Style**: 极简克制阅读界面（Minimal Pure Reader）
**Keywords**: 安静、扁平、留白、信息密度可控、中文语境、无装饰
**Tone**: 克制、专业、编辑室工作台 — NOT 花哨、卡片化、图标化、仪表盘感
**Feel**: 像在用一个只装了纯文本的阅读器：没有边框在提醒你"这是一个容器"，只有间距在告诉你"这是一条新内容"。

**Interaction Tier**: L1 精致静态（这是高频使用的内容浏览/管理工具，不是营销页，动效必须让位于可扫读性）
**Dependencies**: CSS only，不引入 GSAP / Lenis / 任何 JS 动效库

## 2. Color Palette & Roles

```css
:root {
  /* Backgrounds */
  --bg: #fafafa;
  --surface: #ffffff;          /* sidebar 背景、输入框背景 */
  --surface-alt: #f2f2f4;      /* 分组标题条、次级背景 */
  --surface-hover: #f0f0f2;    /* 列表行 hover */

  /* Borders */
  --border: #eaeaec;           /* 只用于 sidebar 与主内容的唯一分割线、分组之间 */
  --border-hover: #d8d8dc;

  /* Text */
  --text: #18181b;             /* 内容标题専用 */
  --text-secondary: #52525b;   /* 正文/摘要 */
  --text-tertiary: #9a9aa2;    /* 来源名、时间、计数——最弱层级 */

  /* Accent */
  --accent: #4f46e5;
  --accent-hover: #4338ca;

  --bg-rgb: 250,250,250;
  --accent-rgb: 79,70,229;

  --success: #16a34a;
  --error: #dc2626;
  --warning: #b45309;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #101012;
    --surface: #17171a;
    --surface-alt: #1c1c20;
    --surface-hover: #202024;
    --border: #232327;
    --border-hover: #333339;
    --text: #f2f2f4;
    --text-secondary: #a8a8b0;
    --text-tertiary: #6c6c76;
    --accent: #818cf8;
    --accent-hover: #a5b4fc;
    --bg-rgb: 16,16,18;
    --accent-rgb: 129,140,248;
    --success: #4ade80;
    --error: #f87171;
    --warning: #fbbf24;
  }
}
```

**Color Rules:**
- 所有颜色通过 CSS 变量引用，禁止硬编码 hex。
- `--border` 全站只出现在三个地方：sidebar 与主内容的竖向分割线、sidebar 内部分组之间的横线、日期分组标题下的横线。列表行之间**不加线**，用间距分隔。
- `--accent` 只用于：当前激活的导航项文字色、链接 hover、聚类数字角标。禁止大面积色块（不再用 accent 做按钮背景）。
- 三级文字层级必须严格执行：内容标题用 `--text`，摘要/正文用 `--text-secondary`，来源名/时间/计数用 `--text-tertiary`。

## 3. Typography Rules

**Font Stack:**
```css
--font-sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
```
不引入 Google Fonts——中文内容为主，系统中文字体（PingFang SC / Noto Sans SC）渲染质量高于任何 Web Font 加载后的中文，且避免闪烁。英文源标题（YouTube/HN 原文）跟随同一 font-stack 的西文回退（system-ui 部分），不单独切字体，保持中英混排统一。

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|-----------------|
| 内容标题（新闻/单条标题） | sans | 15px | 600 | 1.6 | 0 |
| 聚类话题标题 | sans | 15px | 700 | 1.5 | 0 |
| 摘要/综述正文 | sans | 13px | 400 | 1.75 | 0.01em |
| 来源名 / 元信息 | sans | 12px | 400 | 1.5 | 0 |
| 时间 | mono | 11px | 400 | 1.5 | 0 |
| 分组小标题（日期/侧栏分组） | sans | 11px | 600 | 1.4 | 0.04em，大写/加粗代替颜色强调 |
| 侧边栏导航项 | sans | 13px | 400（激活态 600） | 1.5 | 0 |

**Typography Rules:**
- 内容标题 weight ≥ 600，是页面里除分组小标题外唯一允许用高权重的位置——这是"标题优先"的唯一实现手段，不用颜色、不用底色、不用图标强调标题。
- 摘要正文 `line-height: 1.75`，中文长句子在 13px 下必须留够呼吸感。
- **NEVER use**: 衬线字体（本场景是密集信息浏览，非编辑阅读长文，衬线在小字号中文环境可读性差）、任何装饰性 / 手写字体、渐变文字、文字投影。

**Text Decoration:**
- 内容标题：无渐变、无投影（极简克制风格下标题靠字重和字号建立层级，不靠装饰）。
- 聚类数字角标：纯色数字 `--text-tertiary`，不再用色块背景（原设计的灰色方块背景去掉，改为纯文本，冒号或斜体区分即可）。

## 4. Component Stylings

### Sidebar Navigation Item
```css
.nav-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color .12s ease, background-color .12s ease;
}
.nav-item:hover {
  background: var(--surface-hover);
  color: var(--text);
}
.nav-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}
.nav-item.active {
  color: var(--accent);
  font-weight: 600;
  background: transparent; /* 不再用色块，靠文字色+字重区分 */
}
```
所有导航层级（新闻汇总/社媒汇总/重点关注单条/全部信息源单条/数据源管理）复用同一个 `.nav-item` 类，**不做视觉差异化**——差异只体现在它们所在的分组（见下方 Navigation Group）。

### Navigation Group（侧边栏分组）
```css
.nav-group-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--text-tertiary);
  padding: 16px 12px 6px;
  text-transform: none; /* 中文不转大写 */
}
.nav-group + .nav-group {
  border-top: 1px solid var(--border);
  margin-top: 8px;
  padding-top: 8px;
}
```

### Star Toggle（hover 才出现）
```css
.src-row { position: relative; display: flex; align-items: center; gap: 6px; }
.star-btn {
  opacity: 0;
  width: 18px;
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 13px;
  cursor: pointer;
  transition: opacity .12s ease, color .12s ease;
}
.src-row:hover .star-btn,
.star-btn:focus-visible { opacity: 1; }
.star-btn.starred { opacity: 1; color: var(--warning); } /* 已加星的始终可见，只有未加星的才隐藏 */
.star-btn:hover { color: var(--warning); }
```
**关键规则**：只有「未加星」的行才默认隐藏 ☆；已加星的 ★ 常驻可见（否则用户看不出自己星了谁）。hover 或键盘 focus 时未加星行的 ☆ 才浮现。

### List Row（内容行 — 替代原来的 card / bordered item）
```css
.row {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 4px 16px;
  padding: 14px 0;
}
.row + .row { margin-top: 0; } /* 靠 padding 制造间距，不加 border-bottom */
.row:hover { background: var(--surface-hover); margin: 0 -12px; padding: 14px 12px; border-radius: 8px; }
.row-title { font-size: 15px; font-weight: 600; color: var(--text); line-height: 1.6; }
.row-title a { color: inherit; text-decoration: none; }
.row-title a:hover { color: var(--accent); }
.row-meta { display: flex; gap: 8px; align-items: baseline; font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
.row-time { font-family: var(--font-mono); font-size: 11px; }
.row-source { cursor: pointer; }
.row-source:hover { color: var(--accent); }
```
新闻聚类沿用同一个 row 结构，只是标题上多一个「N 个来源」的极简后缀（纯文本，不做数字角标色块）：
```css
.cluster-count-suffix { color: var(--text-tertiary); font-weight: 400; font-size: 12px; }
```
展开的聚类成员列表复用 `.row`（缩进 16px，`padding-left: 16px`），不再单独设计"member"样式。

### Search Input
```css
.search-input {
  width: 100%;
  background: var(--surface-alt);
  border: 1px solid transparent;
  color: var(--text);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-family: var(--font-sans);
}
.search-input:focus { outline: none; border-color: var(--accent); background: var(--surface); }
.search-input::placeholder { color: var(--text-tertiary); }
```

### Links
```css
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; text-underline-offset: 2px; }
```

## 5. Layout Principles

**整体结构**：`position: fixed` 双栏布局，无顶部 header/横幅。

```css
.app { display: flex; height: 100vh; width: 100vw; overflow: hidden; }
.sidebar {
  width: 240px;
  flex-shrink: 0;
  height: 100vh;
  overflow-y: auto;      /* 独立滚动 */
  background: var(--surface);
  border-right: 1px solid var(--border); /* 全站唯一的竖向分割线 */
  padding: 16px 8px;
}
.main {
  flex: 1;
  height: 100vh;
  overflow-y: auto;      /* 主内容独立滚动，跟 sidebar 互不影响 */
  padding: 32px 40px;
}
.main-inner { max-width: 720px; } /* 内容阅读区域窄一点，行长可控在 70-80 字符 */
```

**Container:**
- 主内容阅读宽度：max-width 720px（长文阅读黄金行宽），侧边栏固定 240px。
- 主内容左右 padding：40px（桌面），16px（移动端）。

**Spacing Scale:**
- 行间距（row 之间）：14px 上下 padding，无额外 margin。
- 分组间距（日期组之间）：32px。
- 侧栏分组间距：16px + 1px 分割线。
- 页面级留白：主内容顶部 32px（用来替代原来的 header 高度，给视觉呼吸感，不是标题栏）。

**Grid:**
```css
.row { grid-template-columns: 56px 1fr; }      /* 时间列固定56px，内容自适应 */
```
社媒/频道列表用 grid 固定时间列宽度对齐；新闻聚类不需要时间列（聚类没有单一时间），改用 `grid-template-columns: 1fr`。

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | 无阴影、无边框 | 列表行默认态、sidebar 导航项默认态——页面 99% 的元素 |
| Hint | `background: var(--surface-hover)` 纯色块，无阴影 | 行 hover、导航项 hover |
| Divider | `1px solid var(--border)` | 仅限：sidebar/main 竖向分割线、sidebar 分组分割线、日期组标题下划线 |

不使用 `box-shadow`。这是本设计的核心护栏——去卡片化意味着彻底放弃阴影语言，纯用背景色块 + 间距建立层次。

## 7. Animation & Interaction

**Motion Philosophy**: 只用于确认"这里可以点"，不用于吸引注意力。
**Tier**: L1

### Base Setup
无需 JS 动效初始化，纯 CSS transition。

### Entrance Animation
不做入场动画——这是数据浏览工具，切换 tab/筛选时内容应该**立即**出现，任何淡入延迟都是对高频操作的阻力。

### Hover & Focus States
```css
.row:hover, .nav-item:hover, .search-input:focus { transition: background-color .12s ease, color .12s ease; }
.star-btn { transition: opacity .12s ease, color .12s ease; }
a:hover { transition: color .12s ease; }
```
所有 transition 统一 120ms，`ease`，不用弹性/回弹曲线——保持"安静"的调性。

### Special Effects
无。不加光标跟随、不加视差、不加背景动画。

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
```

## 8. Do's and Don'ts

### Do
- 内容标题永远是一行里字号最大、字重最高的元素。
- 三级文字色（text / text-secondary / text-tertiary）严格对应"标题 / 摘要 / 元信息"三层语义，不混用。
- 侧边栏所有导航层级共用同一套 `.nav-item` 样式，只用分组间距和小标题区分类别。
- 星标默认隐藏，行 hover 或键盘 focus 时浮现；已加星的常驻可见。
- 用间距（padding/margin）分隔列表项，而不是边框线。
- sidebar 和主内容各自独立 `overflow-y: auto`，滚动互不干扰。
- 中英混排的原始标题（英文源）保持原文，不强行翻译失真；界面控件文案、分组标签、空状态提示全部中文。

### Don't
- ❌ 不加顶部 header/标题横幅——导航从 sidebar 顶部直接开始。
- ❌ 不用 `box-shadow`，不用卡片背景色+边框的组合（不做"card"容器）。
- ❌ 列表行之间不加 `border-bottom` 分割线。
- ❌ 不同导航项（新闻/社媒/频道/信息源/管理）不使用不同的强调色或图标做区分。
- ❌ 不使用任何装饰性 emoji（📰📱📌⚙️等）；★/☆ 是功能控件，允许保留。
- ❌ 聚类数字/来源计数不用色块角标，只用纯文本弱化展示。
- ❌ 星标图标不常驻显示（未加星状态必须默认隐藏）。
- ❌ 不引入渐变文字、文字投影、衬线字体。
- ❌ 不做入场动画/滚动 reveal——这是工具类页面，不是展示页。

## 9. Responsive Behavior

**Breakpoints:**
| Name | Width | Key Changes |
|------|-------|--------------|
| Desktop | > 860px | 双栏布局，sidebar 240px 固定 + 主内容自适应 |
| Mobile | ≤ 860px | sidebar 收起为顶部横向 tab 条（仅顶层：新闻汇总/社媒汇总/数据源管理），"重点关注"与"全部信息源"两个子列表在移动端折叠进"数据源管理"页统一管理，不在顶部横向条里堆栈 |

**Touch Targets:** 最小 40×40px（导航项、星标按钮的可点击热区通过 padding 撑到 40px，不只是视觉图标本身的尺寸）。
**Collapsing Strategy:** 移动端 `.app` 改 `flex-direction: column`；`.sidebar` 变为 `height: auto; overflow-x: auto; overflow-y: visible`，只保留顶层三个入口横向排列；主内容 `padding: 20px 16px`；`.row` 的 grid 时间列在 ≤600px 时改为纵向堆叠（时间在标题上方一行，弱化显示）。
