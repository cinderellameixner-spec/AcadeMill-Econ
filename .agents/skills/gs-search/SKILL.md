---
name: gs-search
description: "Search Google Scholar for academic papers by keywords. Returns results with title, authors, journal, year, citation count, and full-text links. Use when the user wants to search Google Scholar."
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


# Google Scholar Basic Search

Search Google Scholar for papers using keyword(s). Returns structured result list via DOM scraping.

## Arguments

用户本次请求中的参数 contains the search keyword(s).

## Steps

### 1. Navigate

Use `mcp__gs-browser__navigate_page`:
- url: `https://scholar.google.com/scholar?q={URL_ENCODED_KEYWORDS}&hl=en&num=10`

### 2. Extract results (evaluate_script)

Wait for results to load, check for CAPTCHA, then scrape the DOM:

```javascript
async () => {
  // Wait for results or CAPTCHA
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('#gs_res_ccl') || document.querySelector('#gs_captcha_ccl')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  // CAPTCHA check
  if (document.querySelector('#gs_captcha_ccl') || document.body.innerText.includes('unusual traffic')) {
    return { error: 'captcha', message: 'Google Scholar requires CAPTCHA verification. Please complete it in your browser, then tell me to continue.' };
  }

  const items = document.querySelectorAll('#gs_res_ccl .gs_r.gs_or.gs_scl');
  const results = Array.from(items).map((item, i) => {
    const titleEl = item.querySelector('.gs_rt a');
    const meta = item.querySelector('.gs_a')?.textContent || '';
    // Parse "Author1, Author2 - Journal, Year - publisher"
    const parts = meta.split(' - ');
    const authors = parts[0]?.trim() || '';
    const journalYear = parts[1]?.trim() || '';
    const citedByEl = item.querySelector('.gs_fl a[href*="cites"]');
    const relatedEl = item.querySelector('.gs_fl a[href*="related"]');
    const versionsEl = item.querySelector('.gs_fl a[href*="cluster"]');

    return {
      n: i + 1,
      title: titleEl?.textContent?.trim() || item.querySelector('.gs_rt')?.textContent?.trim() || '',
      href: titleEl?.href || '',
      authors,
      journalYear,
      citedBy: citedByEl?.textContent?.match(/\d+/)?.[0] || '0',
      citedByUrl: citedByEl?.href || '',
      dataCid: item.getAttribute('data-cid') || '',
      fullTextUrl: (item.querySelector('.gs_ggs a') || item.querySelector('.gs_or_ggsm a'))?.href || '',
      snippet: item.querySelector('.gs_rs')?.textContent?.trim()?.substring(0, 200) || '',
      relatedUrl: relatedEl?.href || '',
      versionsUrl: versionsEl?.href || '',
      versions: versionsEl?.textContent?.match(/\d+/)?.[0] || ''
    };
  });

  const totalText = document.querySelector('#gs_ab_md')?.textContent?.trim() || '';
  const currentUrl = window.location.href;
  return { total: totalText, resultCount: results.length, currentUrl, results };
}
```

### 3. Report

Present results as a numbered list:

```
Searched Google Scholar for "用户本次请求中的参数": {total}

1. {title}
   Authors: {authors} | {journalYear}
   Cited by: {citedBy} | [Full text]({fullTextUrl})
   Data-CID: {dataCid}

2. ...
```

Always show the `dataCid` — it's the unique identifier used for citation export and "cited by" tracking.

If `fullTextUrl` is available, highlight it (means open-access PDF/HTML).

### 4. Follow-up

When the user wants to:
- **See more results**: use `gs-navigate-pages` to go to next page
- **See who cited a paper**: use `gs-cited-by` with the data-cid
- **Export to Zotero**: use `gs-export` with the data-cid(s)

## CAPTCHA Handling

If the result contains `{error: 'captcha'}`:
1. Tell the user: "Google Scholar is requesting CAPTCHA verification. Please complete it in your browser."
2. Wait for user confirmation
3. Retry the evaluate_script extraction

## Notes

- This skill uses 2 tool calls: `navigate_page` + `evaluate_script`
- Google Scholar has NO public API — all data extraction is via DOM scraping
- `data-cid` is the primary identifier (cluster ID) — used across all GS skills
- Keep request frequency low to avoid triggering CAPTCHA
- Default `num=10` results per page (max 20)
