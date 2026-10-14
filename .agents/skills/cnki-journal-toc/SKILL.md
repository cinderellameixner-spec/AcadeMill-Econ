---
name: cnki-journal-toc
description: "Browse journal issues, view table of contents, and download original TOC PDF from CNKI. Use when user wants to see papers in a specific journal issue or download the original cover/TOC pages."
---

## Codex 执行约定

以当前可用工具为准：文档里的 MCP 工具名是能力提示，先核对真实工具名称、参数和返回结果。工具缺失就报告缺失，不声称已检索、归档或生成文件。
按本次任务读取所需参考段落，不要一次加载全部模块。用户级 Claude 配置只作迁移来源，不在新项目中修改。
中文触发词直接路由；原先的 Task/agent 调用表示工作流职责，不意味着必须创建子代理。
不编造文献、DOI、系数、样本量或显著性；事实与推测分开，数据缺失时标明待补。
Word、PowerPoint、PDF 成稿按当前环境实际可用的文档/演示/PDF技能交付；找不到工具时提供明确的文本或源码产物，不能把大纲称为已生成的文件。旧文档中的 anthropics/skills 等为可选旧集成，不自动安装。

浏览器服务：`cnki-browser`（Microsoft Edge）。先按 [校园文献检索路径](../../../docs/LITERATURE_SEARCH.md) 打开浙大 WebVPN，等待用户手动登录，再从电子资源导航进入 CNKI；有效登录复用同一会话。
校园路径优先于本文件旧公网 URL、固定 API 与导航说明。保留页面实际代理链接，先从当前界面点击功能入口；代理页面未核对兼容前不执行旧脚本，不用公网直链替换校园链接。
页面选择器可能随站点更新；先检查当前页面，不盲目执行旧选择器。验证码交给用户完成；付费下载逐篇确认。
文中的 JavaScript 是浏览器工具调用示例，不是随仓库安装的独立脚本；执行前核对实际工具接口与页面。临时文件放所属研究 `work/`。


# CNKI Journal Table of Contents (期刊目录浏览 + 原版目录下载)

Browse journal issues, extract the paper list, and optionally open/download the original TOC PDF (封面+目录扫描版).

## Arguments

`用户本次请求中的参数` describes what to browse:
- `{journal name}` — which journal
- `{year}` (optional) — which year, defaults to latest
- `{issue}` (optional) — which issue number
- `download` (optional) — if included, download the original TOC PDF

Examples:
- `计算机学报 2026 01期` — browse 2026 issue 1
- `计算机学报 2026 01期 download` — download original TOC PDF
- `计算机学报` — shows latest (网络首发)

## Steps

### 1. Navigate to journal detail page

If not already on a journal detail page (`navi.cnki.net/knavi/detail`):
- Use `cnki-journal-search` to find the journal
- Use `mcp__cnki-browser__list_pages` + `mcp__cnki-browser__select_page` to switch to the journal detail tab (opens in new tab)

### 2. Select issue + extract papers (single async evaluate_script)

Replace `YEAR` and `ISSUE` with actual values (e.g., `"2025"`, `"No.01"`).
The "刊期浏览" tab is the default active view — no need to click it.

```javascript
async () => {
  const year = "YEAR";
  const issue = "ISSUE"; // Format: "No.01", "No.12", etc.

  const dls = document.querySelectorAll('#yearissue0 dl.s-dataList');
  let target = null;
  for (const dl of dls) {
    if (dl.querySelector('dt')?.innerText?.trim() === year) {
      target = Array.from(dl.querySelectorAll('dd a')).find(a => a.innerText.trim() === issue);
      break;
    }
  }
  if (!target) {
    // Return available years and issues for the requested year
    const available = Array.from(dls).map(dl => ({
      year: dl.querySelector('dt')?.innerText?.trim(),
      issues: Array.from(dl.querySelectorAll('dd a')).map(a => a.innerText.trim())
    })).filter(y => y.year);
    return { error: 'issue_not_found', year, issue, available: available.slice(0, 5) };
  }

  target.click();

  // Wait for paper list to load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      const rows = document.querySelectorAll('#CataLogContent dd.row');
      if (rows.length > 0) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    setTimeout(c, 1000);
  });

  // Extract papers
  const rows = document.querySelectorAll('#CataLogContent dd.row');
  const papers = Array.from(rows).map((dd, i) => ({
    no: i + 1,
    title: dd.querySelector('span.name a')?.innerText?.trim(),
    authors: dd.querySelector('span.author')?.innerText?.trim()?.replace(/;$/, ''),
    pages: dd.querySelector('span.company')?.innerText?.trim()
  }));

  // Get 原版目录 URL
  const tocBtn = document.querySelector('a.btn-preview:not(.btn-back)');

  return {
    issueLabel: document.querySelector('span.date-list')?.innerText?.trim(),
    paperCount: papers.length,
    papers,
    tocUrl: tocBtn?.href || null,
    url: location.href
  };
}
```

### 3. Present results

```
## {journal_name} — {issueLabel}

共 {paperCount} 篇论文：

1. {title}  [pp. {pages}]
   作者：{authors}

2. {title}  [pp. {pages}]
   作者：{authors}
...
```

### 4. Download original TOC PDF (if requested)

If user requested download, or asks for "原版目录":

**Method A — Click "原版目录浏览" to open reader, then download:**

1. Find the `link` with text "原版目录浏览" in the snapshot (class `btn-preview`)
2. Click it — this opens a new tab with the reader page (`kns.cnki.net/reader/report`)
3. Use `mcp__cnki-browser__list_pages` to find the new reader tab
4. Use `mcp__cnki-browser__select_page` to switch to it
5. Use `mcp__cnki-browser__wait_for` with text `["下载"]`
6. Take snapshot — find the `link` with text "下载" (the download button in the reader toolbar)
7. Click the download link — triggers PDF download via Edge

**Method B — Direct download from reader page:**

If already on a reader page (`kns.cnki.net/reader/report`):
1. Take snapshot
2. Find `link` with text "下载"
3. Click it

After clicking, inform the user:
> 原版目录 PDF 下载已触发，请在 Edge 下载管理器中查看。

## Tool calls

- Browse issue: 1 (evaluate_script only) — after navigating to journal page
- Download TOC: requires snapshot + click + tab switching (new tab)

## Verified selectors

### Journal Detail — 刊期浏览

| Element | Selector | Notes |
|---------|----------|-------|
| 刊期浏览 tab | `a` text "刊期浏览" | default active (`li.on.cur`), no need to click |
| Year area | `#yearissue0` / `.yearissuepage` | |
| Year groups | `dl.s-dataList` | inside `#yearissue0` |
| Year label | `dl.s-dataList dt` | text "2026", "2025" etc. |
| Issue links | `dl.s-dataList dd a` | text "No.01", "No.12" etc. |
| Issue label | `span.date-list` | text "2025年01期" |
| Paper container | `#CataLogContent` | |
| Paper entries | `#CataLogContent dd.row` | |
| Paper title | `dd.row span.name a` | href to `kcms2/article/abstract` |
| Paper authors | `dd.row span.author` | semicolon-separated |
| Paper page range | `dd.row span.company` | class is "company" but holds page range |
| Paper ID | `dd.row b[name="encrypt"]` | id like "JSJX202512001" |
| 原版目录浏览 | `a.btn-preview:not(.btn-back)` | href to `bar.cnki.net/bar/download/order` |
| 返回 | `a.btn-preview.btn-back` | |

### Reader Page (kns.cnki.net/reader/report)

| Element | Pattern |
|---------|--------|
| Page title | `RootWebArea "期刊原版目录"` |
| Download button | `link` text "下载", URL to `bar.cnki.net/bar/download/order` |
| Current page | `textbox` value (page number) |
| Total pages | `StaticText` (e.g., "4") |
| Navigation | `generic` description "上一页" / "下一页" |

## Important Notes

- "原版目录浏览" only appears when a **specific issue** is selected (not for 网络首发 view).
- The reader page opens in a **new tab**.
- The download link in the reader requires login. If download fails, remind user to log in.
- The download URL is session-specific — do not cache or reuse.
