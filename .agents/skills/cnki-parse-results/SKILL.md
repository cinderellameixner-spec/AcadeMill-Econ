---
name: cnki-parse-results
description: "Parse current CNKI search results page into structured paper data (title, authors, journal, date, citations). Use after a search has been performed and you need to extract the results."
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


# CNKI Parse Search Results

Extract structured paper data from the current CNKI search results page.

## Prerequisites

The current Edge page must show CNKI search results and the result count. WebVPN URLs may omit `kns.cnki.net`; use the navigation origin and actual page content to identify the results.

## Steps

### 1. Verify we are on a results page

Use `mcp__cnki-browser__take_snapshot`. Verify the page contains "条结果". If not, inform the user that no search results page is currently open.

If captcha text is found, verify that the challenge is actually visible using a screenshot or DOM bounds and computed visibility before asking the user. A preloaded off-screen container near top -1000000 is not an active captcha. Stop only for a displayed challenge; do not expose or manipulate hidden captcha components.

### 2. Extract results via JavaScript

Use `mcp__cnki-browser__evaluate_script` with this function:

```javascript
() => {
  const rows = document.querySelectorAll('.result-table-list tbody tr');
  const checkboxes = document.querySelectorAll('.result-table-list tbody input.cbItem');
  const results = Array.from(rows).map((row, index) => {
    const nameCell = row.querySelector('td.name');
    const titleLink = nameCell?.querySelector('a.fz14');
    const authorCell = row.querySelector('td.author');
    const sourceCell = row.querySelector('td.source');
    const dateCell = row.querySelector('td.date');
    const dataCell = row.querySelector('td.data');
    const quoteCell = row.querySelector('td.quote');
    const downloadCell = row.querySelector('td.download');
    const isOnlineFirst = !!nameCell?.querySelector('.marktip');

    return {
      number: index + 1,
      title: titleLink?.innerText?.trim() || '',
      url: titleLink?.href || '',
      exportId: checkboxes[index]?.value || '',
      authors: Array.from(authorCell?.querySelectorAll('a.KnowledgeNetLink') || []).map(a => a.innerText?.trim()),
      journal: sourceCell?.querySelector('a')?.innerText?.trim() || '',
      date: dateCell?.innerText?.trim() || '',
      database: dataCell?.innerText?.trim() || '',
      citations: quoteCell?.innerText?.trim() || '',
      downloads: downloadCell?.innerText?.trim() || '',
      isOnlineFirst: isOnlineFirst
    };
  });

  const totalText = document.querySelector('.pagerTitleCell')?.innerText || '';
  const totalMatch = totalText.match(/([\d,]+)/);
  const pageInfo = document.querySelector('.countPageMark')?.innerText || '';

  return {
    papers: results,
    totalCount: totalMatch ? totalMatch[1] : 'unknown',
    pageInfo: pageInfo
  };
}
```

### 3. Present results

Format as a numbered list:

```
CNKI search results ({totalCount} total, page {pageInfo}):

1. {title} {isOnlineFirst ? "[网络首发]" : ""}
   Authors: {authors joined by "; "}
   Journal: {journal} | Date: {date} | Type: {database}
   Citations: {citations} | Downloads: {downloads}
   URL: {url}

2. ...
```

### 4. Fallback: snapshot-based parsing

If JavaScript returns empty (DOM structure changed), use `mcp__cnki-browser__take_snapshot` and parse the accessibility tree manually:

Look for the repeating pattern:
- `checkbox` → `StaticText` (number) → `link` with URL containing `kcms2/article/abstract` (title) → `link`s with URL containing `kcms2/author/detail` (authors) → `link` with URL containing `navi.cnki.net/knavi/detail` (journal) → `StaticText` (date) → `StaticText` (database type)

## Verified DOM Selectors (CNKI uses jQuery, stable semantic class names)

| Data       | Selector                         | Notes                      |
|------------|----------------------------------|----------------------------|
| Table      | `.result-table-list tbody tr`    | Each row = one paper       |
| Checkbox   | `input.cbItem`                   | value = export encrypted ID |
| Number     | `td.seq`                         | Row sequence number        |
| Title      | `td.name a.fz14`                 | Paper title link           |
| Authors    | `td.author a.KnowledgeNetLink`   | Author name links          |
| Journal    | `td.source a`                    | Journal/source link        |
| Date       | `td.date`                        | Publication date text      |
| DB Type    | `td.data`                        | Database type (期刊/学位论文) |
| Citations  | `td.quote`                       | Citation count             |
| Downloads  | `td.download`                    | Download count             |
| Online 1st | `td.name .marktip`               | "网络首发" label            |
| Total      | `.pagerTitleCell`                 | "共找到 X 条结果"           |
| Page       | `.countPageMark`                  | "1/300" format             |
