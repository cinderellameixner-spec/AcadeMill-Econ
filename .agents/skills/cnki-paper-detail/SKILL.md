---
name: cnki-paper-detail
description: "Extract full paper details from a CNKI paper page including title, authors, affiliations, abstract, keywords, fund, classification. Use when the user needs detailed information about a specific paper."
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


# CNKI Paper Detail Extraction

Extract complete metadata from a CNKI paper detail page.

## Arguments

`用户本次请求中的参数` is optionally a CNKI paper detail URL (containing `kcms2/article/abstract`). If not provided, assumes the current page is already a paper detail page.

## Steps

### 1. Navigate to the paper page (if URL provided)

If `用户本次请求中的参数` contains a URL:
- Use `mcp__cnki-browser__navigate_page` with the URL.
- Use `mcp__cnki-browser__wait_for` with text `["摘要"]` and timeout 15000.

### 2. Check for captcha

Use `mcp__cnki-browser__take_snapshot`. If "拖动下方拼图完成验证" is found, verify that the challenge is displayed using a screenshot or DOM bounds and computed visibility. Preloaded off-screen text near top -1000000 is not an active captcha. Do not expose hidden components. Only for an actually displayed challenge, notify the user:

> CNKI 正在显示滑块验证码。请在 Edge 浏览器中手动完成拼图验证，完成后告诉我继续。

### 3. Extract paper metadata via JavaScript

Use `mcp__cnki-browser__evaluate_script` with this function:

```javascript
() => {
  const brief = document.querySelector('.brief');
  if (!brief) return { error: 'Paper detail section (.brief) not found' };

  // Title
  const title = brief.querySelector('h1')?.innerText?.trim()
    ?.replace(/\s*附视频\s*$/, '')  // remove "附视频" suffix
    ?.replace(/\s*网络首发\s*$/, ''); // remove "网络首发" suffix

  // Authors - first h3.author contains author links with sup tags
  const authorH3s = brief.querySelectorAll('h3.author');
  const authorSection = authorH3s[0];
  const authors = [];
  if (authorSection) {
    const authorLinks = authorSection.querySelectorAll('a');
    authorLinks.forEach(a => {
      const name = a.innerText?.replace(/\d+$/, '').trim();
      const supMatch = a.innerText?.match(/(\d+)$/);
      const affiliationNum = supMatch ? supMatch[1] : '';
      authors.push({ name, affiliationNum });
    });
  }

  // Affiliations - second h3.author contains org links
  const affiliations = [];
  if (authorH3s.length > 1) {
    const orgLinks = authorH3s[1].querySelectorAll('a');
    orgLinks.forEach(a => {
      affiliations.push(a.innerText?.trim());
    });
  }

  // Abstract
  const abstractEl = document.querySelector('.abstract-text');
  const abstract = abstractEl?.innerText?.trim() || '';

  // Keywords
  const keywordsP = document.querySelector('p.keywords');
  const keywords = keywordsP
    ? Array.from(keywordsP.querySelectorAll('a')).map(a => a.innerText?.replace(/;$/, '').trim())
    : [];

  // Fund
  const fundsP = document.querySelector('p.funds');
  const fund = fundsP?.innerText?.trim() || '';

  // Classification code
  const clcCode = document.querySelector('.clc-code');
  const classification = clcCode?.innerText?.trim() || '';

  // Journal/source
  const docTop = document.querySelector('.doc-top');
  const journal = docTop?.querySelector('a')?.innerText?.trim() || '';

  // Online first / publication info
  const headTime = document.querySelector('.head-time');
  const pubInfo = headTime?.innerText?.trim() || '';

  // Is online first?
  const isOnlineFirst = !!brief.querySelector('.icon-shoufa');

  // Article outline/TOC
  const catalogList = document.querySelector('.catalog-list, .catalog-listDiv');
  const toc = catalogList?.innerText?.trim() || '';

  // Citation network counts
  const citationTabs = document.querySelectorAll('ul.module-tab.tpl_lieteratures li');
  const citationInfo = {};
  citationTabs.forEach(li => {
    const id = li.getAttribute('data-id');
    const text = li.innerText?.trim();
    const countMatch = text.match(/(\d+)/);
    if (id) {
      citationInfo[id] = {
        label: text.replace(/\d+/, '').trim(),
        count: countMatch ? parseInt(countMatch[1]) : 0
      };
    }
  });

  return {
    title,
    authors,
    affiliations,
    abstract,
    keywords,
    fund,
    classification,
    journal,
    pubInfo,
    isOnlineFirst,
    toc,
    citationInfo
  };
}
```

### 4. Format and present the output

```
## {title} {isOnlineFirst ? "[网络首发]" : ""}

**Authors:**
{For each author: "- {name} ({affiliation})"}

**Affiliations:**
{For each affiliation: "- {affiliation}"}

**Journal:** {journal}
**Publication Info:** {pubInfo}

**Abstract:**
{abstract}

**Keywords:** {keywords joined by ", "}

**Fund:** {fund}
**Classification:** {classification}

**Citation Network:**
{For each citation type: "- {label}: {count}"}
```

### 5. Fallback: snapshot-based parsing

If JS extraction fails, use `mcp__cnki-browser__take_snapshot` and parse the accessibility tree:
- **Title**: `heading` level 1 element
- **Authors**: `link` elements whose URLs contain `kcms2/author/detail`
- **Affiliations**: `link` elements whose URLs contain `kcms2/organ/detail`
- **Abstract**: `StaticText` following "摘要："
- **Keywords**: `link` elements whose URLs contain `kcms2/keyword/detail`
- **Fund**: `link` elements following "基金资助："
- **Classification**: `StaticText` following "分类号："

## Verified DOM Selectors

| Data           | Selector                                   | Notes                                    |
|----------------|--------------------------------------------|------------------------------------------|
| Paper section  | `.brief`                                    | Main paper info container                |
| Title          | `.brief h1`                                 | May contain icons, clean text needed     |
| Authors        | `.brief h3.author:first-of-type a`          | Text has superscript numbers (e.g., "张三1") |
| Affiliations   | `.brief h3.author:nth-of-type(2) a`         | Text starts with "N." (e.g., "1.北京大学") |
| Abstract       | `.abstract-text`                            | Full abstract text                       |
| Keywords       | `p.keywords a`                              | Semicolon-separated keyword links        |
| Fund           | `p.funds`                                   | Fund information text                    |
| Classification | `.clc-code`                                 | CLC classification codes                |
| Journal        | `.doc-top a`                                | Source journal link                      |
| Online first   | `.brief .icon-shoufa`                       | Present if paper is online first         |
| Citation tabs  | `ul.module-tab.tpl_lieteratures li`         | data-id attr identifies type             |
