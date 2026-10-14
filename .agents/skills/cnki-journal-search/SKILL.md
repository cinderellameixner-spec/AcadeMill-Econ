---
name: cnki-journal-search
description: "Search for journals/publications on CNKI by name, ISSN, CN, or sponsor. Use when the user wants to find a specific journal or browse publications."
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


# CNKI Journal Search (期刊检索)

## Arguments

`用户本次请求中的参数` is a journal name, ISSN, CN number, or sponsor name.

## Steps

### 1. Navigate

从浙大电子资源导航进入 CNKI，再点击当前资源页的期刊/出版物导航入口；保留页面实际链接，不硬编码公网地址。

### 2. Search + extract results (single evaluate_script, NO wait_for)

Use `mcp__cnki-browser__evaluate_script`. Replace `QUERY_HERE` with actual search term:

```javascript
async () => {
  const query = "QUERY_HERE";

  // Wait for page load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => { if (document.querySelector('input.researchbtn')) r(); else if (++n > 30) j('timeout'); else setTimeout(c, 500); };
    c();
  });

  // Check captcha (visible on screen, not hidden SDK at top:-1000000)
  const outer = document.querySelector('#tcaptcha_transform_dy');
  if (outer && outer.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  // Auto-detect search type and fill
  const select = document.querySelector('select');
  if (select) {
    if (/^\d{4}-\d{3}[\dXx]$/.test(query)) select.value = 'ISSN';
    else if (/^\d{2}-\d{4}/.test(query)) select.value = 'CN';
    select.dispatchEvent(new Event('change', { bubbles: true }));
  }

  const input = document.querySelector('input[placeholder*="检索词"]');
  if (input) input.value = query;

  // Click search button (verified selector: input.researchbtn)
  document.querySelector('input.researchbtn')?.click();

  // Wait for results
  await new Promise((r, j) => {
    let n = 0;
    const c = () => { if (document.body.innerText.includes('条结果')) r(); else if (++n > 30) j('timeout'); else setTimeout(c, 500); };
    c();
  });

  // Click 期刊 tab to filter journals only
  const tabs = document.querySelectorAll('li a');
  for (const a of tabs) { if (a.innerText.trim() === '期刊') { a.click(); break; } }
  await new Promise(r => setTimeout(r, 1500));

  // Extract journal results
  const body = document.body.innerText;
  const countMatch = body.match(/共\s*(\d+)\s*条结果/) || body.match(/找到\s*(\d+)\s*条结果/);
  const count = countMatch ? parseInt(countMatch[1]) : 0;

  const results = [];
  const titleLinks = document.querySelectorAll('a[href*="knavi/detail"]');
  titleLinks.forEach(link => {
    const text = link.innerText?.trim();
    if (!text || text.length < 2) return;
    const parent = link.closest('li, .list-item') || link.parentElement?.parentElement;
    const pt = parent?.innerText || '';
    results.push({
      name: text.split('\n')[0]?.trim(),
      url: link.href,
      issn: pt.match(/ISSN[：:]\s*(\S+)/)?.[1] || '',
      cn: pt.match(/CN[：:]\s*(\S+)/)?.[1] || '',
      cif: pt.match(/复合影响因子[：:]\s*([\d.]+)/)?.[1] || '',
      aif: pt.match(/综合影响因子[：:]\s*([\d.]+)/)?.[1] || '',
      citations: pt.match(/被引次数[：:]\s*([\d,]+)/)?.[1] || '',
      downloads: pt.match(/下载次数[：:]\s*([\d,]+)/)?.[1] || '',
      sponsor: pt.match(/主办单位[：:]\s*(.+?)(?=\n|ISSN)/)?.[1]?.trim() || ''
    });
  });

  return { query, count, results };
}
```

### 3. Present results

```
期刊检索 "用户本次请求中的参数"（共 {count} 条）：

1. {name}
   ISSN: {issn} | CN: {cn}
   复合影响因子: {cif} | 综合影响因子: {aif}
   被引: {citations} | 下载: {downloads}
```

## Notes

- Journal detail pages open in **new tab** — use `list_pages` + `select_page`
- If only 1 journal result, can auto-navigate to detail page for `cnki-journal-index`
- Search button selector: `input.researchbtn` (not generic `button`)

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Tencent captcha SDK preloads DOM at `top: -1000000px` (off-screen, not active).
Only return `error: 'captcha'` when `top >= 0` (actually visible to user).

## Tool calls: 2 (navigate + evaluate_script)
