---
name: gs-navigate-pages
description: "Navigate Google Scholar search result pages. Use when user wants to see more results or go to a specific page."
---

## Codex 执行约定

以当前可用工具为准：文档里的 MCP 工具名是能力提示，先核对真实工具名称、参数和返回结果。工具缺失就报告缺失，不声称已检索、归档或生成文件。
按本次任务读取所需参考段落，不要一次加载全部模块。用户级 Claude 配置只作迁移来源，不在新项目中修改。
中文触发词直接路由；原先的 Task/agent 调用表示工作流职责，不意味着必须创建子代理。
不编造文献、DOI、系数、样本量或显著性；事实与推测分开，数据缺失时标明待补。
Word、PowerPoint、PDF 成稿按当前环境实际可用的文档/演示/PDF技能交付；找不到工具时提供明确的文本或源码产物，不能把大纲称为已生成的文件。旧文档中的 anthropics/skills 等为可选旧集成，不自动安装。

浏览器服务：`gs-browser`。知网用 Edge（校园资源入口）；Google Scholar 用 Chrome。
页面选择器可能随站点更新；先检查当前页面，不盲目执行旧选择器。验证码交给用户完成；付费下载逐篇确认。
文中的 JavaScript 是浏览器工具调用示例，不是随仓库安装的独立脚本；执行前核对实际工具接口与页面。临时文件放所属研究 `work/`。


# Google Scholar Navigate Pages

Navigate search result pages. Requires context from a previous gs-search or gs-advanced-search call.

## Arguments

用户本次请求中的参数 can be:
- `next` — go to next page
- `previous` — go to previous page
- `page N` — go to page N

## Prerequisites

This skill requires context from a previous search:
- `currentUrl`: the current Google Scholar search URL
- `page`: current page number (1-based)

## Steps

### 1. Calculate new URL

Google Scholar uses `start` parameter for pagination (0-indexed, increments of 10):
- Page 1: `start=0` (or omitted)
- Page 2: `start=10`
- Page 3: `start=20`

Based on 用户本次请求中的参数:
- `next`: newStart = currentStart + 10
- `previous`: newStart = max(0, currentStart - 10)
- `page N`: newStart = (N - 1) * 10

Modify the `start` parameter in the current search URL. If `start` doesn't exist in the URL, append `&start={newStart}`.

### 2. Navigate

Use `mcp__gs-browser__navigate_page` with the updated URL.

### 3. Extract results (evaluate_script)

Same extraction script as gs-search step 2:

```javascript
async () => {
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('#gs_res_ccl') || document.querySelector('#gs_captcha_ccl')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  if (document.querySelector('#gs_captcha_ccl') || document.body.innerText.includes('unusual traffic')) {
    return { error: 'captcha', message: 'Google Scholar requires CAPTCHA verification. Please complete it in your browser, then tell me to continue.' };
  }

  const items = document.querySelectorAll('#gs_res_ccl .gs_r.gs_or.gs_scl');
  const results = Array.from(items).map((item, i) => {
    const titleEl = item.querySelector('.gs_rt a');
    const meta = item.querySelector('.gs_a')?.textContent || '';
    const parts = meta.split(' - ');
    const authors = parts[0]?.trim() || '';
    const journalYear = parts[1]?.trim() || '';
    const citedByEl = item.querySelector('.gs_fl a[href*="cites"]');

    return {
      n: NEW_START + i + 1,
      title: titleEl?.textContent?.trim() || item.querySelector('.gs_rt')?.textContent?.trim() || '',
      href: titleEl?.href || '',
      authors,
      journalYear,
      citedBy: citedByEl?.textContent?.match(/\d+/)?.[0] || '0',
      citedByUrl: citedByEl?.href || '',
      dataCid: item.getAttribute('data-cid') || '',
      fullTextUrl: (item.querySelector('.gs_ggs a') || item.querySelector('.gs_or_ggsm a'))?.href || '',
      snippet: item.querySelector('.gs_rs')?.textContent?.trim()?.substring(0, 200) || ''
    };
  });

  const totalText = document.querySelector('#gs_ab_md')?.textContent?.trim() || '';
  const hasNext = !!document.querySelector('#gs_n a.gs_ico_nav_next, #gs_nm a:last-child');
  const currentUrl = window.location.href;
  return { total: totalText, page: NEW_PAGE, resultCount: results.length, hasNext, currentUrl, results };
}
```

Replace `NEW_START` and `NEW_PAGE` with the computed values.

### 4. Report

```
Page {page} for "{query}" ({total}):

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy}
   Data-CID: {dataCid}

2. ...

{hasNext ? "More results available — ask me for the next page." : "No more results."}
```

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- Google Scholar shows 10 results per page by default
- `start` parameter controls pagination offset
