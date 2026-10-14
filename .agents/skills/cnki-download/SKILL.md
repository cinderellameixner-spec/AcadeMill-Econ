---
name: cnki-download
description: "Download a paper PDF/CAJ from CNKI. Requires user to be logged in. Use when user wants to download a specific paper."
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


# CNKI Paper Download (文献下载)

## Prerequisites

用户已在同一 Microsoft Edge 会话登录浙大 WebVPN，从电子资源导航进入 CNKI，并核对校园下载权限；数据库额外认证按实际页面提示由用户手动完成。

## Arguments

`用户本次请求中的参数` is optionally a paper detail URL. If blank, uses current page.

## Steps

### 1. Navigate (if URL provided)

优先从当前校园结果页点击论文链接。已有 URL 时，先核对是否为当前会话的校园资源链接；未代理的公网 URL 只用于识别文献，在校园入口内查找并打开对应记录。

若打开新标签页，用实际 list_pages / select_page 工具选择论文页，保留代理路径与同一 Edge 会话。

### 2. Check status and download (single async evaluate_script)

Replace `FORMAT` with `"pdf"` or `"caj"`:

```javascript
async () => {
  // Wait for page load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      if (document.querySelector('.brief h1')) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    c();
  });

  // Captcha check
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) {
    return { error: 'captcha', message: 'CNKI 正在显示滑块验证码。请在 Edge 中手动完成拼图验证。' };
  }

  const format = "FORMAT"; // "pdf" or "caj"

  // Check download links
  const pdfLink = document.querySelector('#pdfDown') || document.querySelector('.btn-dlpdf a');
  const cajLink = document.querySelector('#cajDown') || document.querySelector('.btn-dlcaj a');

  // Check login status
  const notLogged = document.querySelector('.downloadlink.icon-notlogged')
    || document.querySelector('[class*="notlogged"]');
  if (notLogged) {
    return { error: 'not_logged_in', message: '请检查同一 Edge 的浙大 WebVPN 登录与校园权限；额外认证按页面提示手动完成。' };
  }

  const title = document.querySelector('.brief h1')?.innerText?.trim()?.replace(/\s*网络首发\s*$/, '') || '';

  if (format === 'pdf' && pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (format === 'caj' && cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  } else if (pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  }

  return { error: 'no_download', message: '未找到下载链接', hasPDF: !!pdfLink, hasCAJ: !!cajLink };
}
```

### 3. Report

Based on JS result:
- `status: downloading` → "PDF 下载已触发：{title}。请在 Edge 下载管理器中查看。"
- `error: not_logged_in` → 检查校园会话，失效时返回 WebVPN 等用户手动登录；额外数据库认证按当前页面处理
- `error: captcha` → tell user to solve captcha

## Tool calls: 1–2 (navigate_page if URL + evaluate_script)

## Verified selectors

| Element | Selector | Notes |
|---------|----------|-------|
| PDF download | `#pdfDown` | `<a>` inside `li.btn-dlpdf` |
| CAJ download | `#cajDown` | `<a>` inside `li.btn-dlcaj` |
| Download area | `.download-btns` | parent `<div>` |
| Not logged in | `.downloadlink.icon-notlogged` | |
| Title | `.brief h1` | strip trailing "网络首发" |

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Only active when `top >= 0` (visible). Pre-loaded SDK sits at `top: -1000000px`.
