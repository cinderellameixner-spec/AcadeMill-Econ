---
name: cnki-navigate-pages
description: "Navigate CNKI search result pages (next/previous/specific page) or change sort order. Use when user wants to see more results or change sorting."
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


# CNKI Results Pagination and Sorting

All operations use a single async `evaluate_script` — no snapshot or wait_for needed.

## Arguments

`用户本次请求中的参数` should be one of:
- `next` / `previous` / `page N` — pagination
- `sort by date` / `sort by citations` / `sort by downloads` / `sort by relevance` / `sort by comprehensive` — sorting

## Pagination (single evaluate_script)

Replace `ACTION_HERE` with `"next"`, `"previous"`, or `"page 3"`:

```javascript
async () => {
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  const action = "ACTION_HERE";
  const pageLinks = document.querySelectorAll('.pages a');
  const prevMark = document.querySelector('.countPageMark')?.innerText;

  if (action === 'next') {
    const next = Array.from(pageLinks).find(a => a.innerText.trim() === '下一页');
    if (!next) return { error: 'no_next_page' };
    next.click();
  } else if (action === 'previous') {
    const prev = Array.from(pageLinks).find(a => a.innerText.trim() === '上一页');
    if (!prev) return { error: 'no_previous_page' };
    prev.click();
  } else {
    const num = action.replace(/\D/g, '');
    const target = Array.from(pageLinks).find(a => a.innerText.trim() === num);
    if (!target) return { error: 'page_not_found', available: Array.from(pageLinks).map(a => a.innerText.trim()) };
    target.click();
  }

  // Wait for page change
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      const mark = document.querySelector('.countPageMark')?.innerText;
      if (mark && mark !== prevMark) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    setTimeout(c, 1000);
  });

  const cap2 = document.querySelector('#tcaptcha_transform_dy');
  if (cap2 && cap2.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  return {
    action,
    total: document.querySelector('.pagerTitleCell')?.innerText?.match(/([\d,]+)/)?.[1] || '0',
    page: document.querySelector('.countPageMark')?.innerText || '?',
    url: location.href
  };
}
```

## Sorting (single evaluate_script)

Replace `SORT_HERE` with `"relevance"`, `"date"`, `"citations"`, `"downloads"`, or `"comprehensive"`:

```javascript
async () => {
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  const sortBy = "SORT_HERE";
  const idMap = {
    'relevance': 'FFD', 'date': 'PT',
    'citations': 'CF', 'downloads': 'DFR', 'comprehensive': 'ZH'
  };

  const liId = idMap[sortBy];
  if (!liId) return { error: 'invalid_sort', valid: Object.keys(idMap) };

  const li = document.querySelector('#orderList li#' + liId);
  if (!li) return { error: 'sort_option_not_found' };

  const prevMark = document.querySelector('.countPageMark')?.innerText;
  li.click();

  // Wait for results to refresh (page resets to 1)
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      const mark = document.querySelector('.countPageMark')?.innerText;
      if (mark && mark !== prevMark) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    setTimeout(c, 1000);
  });

  return {
    sortBy,
    total: document.querySelector('.pagerTitleCell')?.innerText?.match(/([\d,]+)/)?.[1] || '0',
    page: document.querySelector('.countPageMark')?.innerText || '?',
    activeLi: document.querySelector('#orderList li.cur')?.innerText?.trim(),
    url: location.href
  };
}
```

## Output

> Navigated to page {page}. Total {total} results.
> Results now sorted by {sortBy}.

## Tool calls: 1 (evaluate_script only)

## Verified selectors

| Element | Selector | Notes |
|---------|----------|-------|
| Page links | `.pages a` | numbers + 上一页/下一页 |
| Current page | `.pages a.cur` | |
| Next page | text `下一页`, class `pagesnums` | |
| Page counter | `.countPageMark` | text "1/300" |
| Sort container | `#sortList` (`.order-group`) | |
| Sort options | `#orderList li` | click to sort |
| 相关度 | `li#FFD` | data-sort="FFD" |
| 发表时间 | `li#PT` | data-sort="PT" |
| 被引 | `li#CF` | data-sort="CF" |
| 下载 | `li#DFR` | data-sort="DFR" |
| 综合 | `li#ZH` | data-sort="ZH" |
| Active sort | `#orderList li.cur` | has class `cur` |

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Only active when `top >= 0` (visible). Pre-loaded SDK sits at `top: -1000000px`.
