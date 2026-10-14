---
name: cnki-journal-index
description: "Query journal indexing/inclusion status on CNKI - check which databases include a journal (北大核心, CSSCI, CSCD, SCI, EI, etc.), get impact factors and evaluation data. Use when user asks about a journal's level, indexing, or ranking."
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


# CNKI Journal Indexing Query (收录查询)

Check which databases index a journal and extract evaluation metrics from its CNKI detail page.

## Arguments

`用户本次请求中的参数` is either:
- A journal name (will search first, then navigate to detail)
- A CNKI journal detail URL (containing `navi.cnki.net/knavi/detail`)

## Steps

### 1. Navigate to the journal detail page

**If URL provided:** Navigate directly.
- Use `mcp__cnki-browser__navigate_page` with the URL.
- Use `mcp__cnki-browser__wait_for` with text `["该刊被以下数据库收录"]` and timeout 15000.

**If journal name provided:** Search first.
- Navigate to `https://navi.cnki.net/knavi`
- Search for the journal (same as cnki-journal-search steps 2-4)
- Click the first matching journal title link
- Use `mcp__cnki-browser__list_pages` to find and select the new detail tab
- Wait for the detail page to load

### 2. Check for captcha

Take snapshot. If "拖动下方拼图完成验证" found, notify user.

### 3. Extract journal info via JavaScript

Use `mcp__cnki-browser__evaluate_script` with this function:

```javascript
() => {
  const body = document.body.innerText;

  // Journal title
  const titleEl = document.querySelector('h3.titbox, h3.titbox1');
  const titleText = titleEl?.innerText?.trim() || '';
  const titleParts = titleText.split('\n').map(s => s.trim()).filter(Boolean);
  const nameCN = titleParts[0] || '';
  const nameEN = titleParts[1] || '';

  // Indexing tags - extract from text between title and "基本信息"
  const tagText = body.match(/Chinese.*?\n\n([\s\S]*?)\n\n基本信息/)?.[1]
    || body.match(new RegExp(nameCN + '[\\s\\S]*?\\n\\n([\\s\\S]*?)\\n\\n基本信息'))?.[1]
    || '';
  const knownTags = ['北大核心','CSSCI','CSCD','SCI','EI','CAS','JST','WJCI','AMI','Scopus','卓越期刊','网络首发'];
  const indexedIn = knownTags.filter(tag => tagText.includes(tag) || body.includes(tag));

  // Basic info
  const sponsor = body.match(/主办单位[：:]\s*(.+?)(?=\n)/)?.[1] || '';
  const frequency = body.match(/出版周期[：:]\s*(\S+)/)?.[1] || '';
  const issn = body.match(/ISSN[：:]\s*(\S+)/)?.[1] || '';
  const cn = body.match(/CN[：:]\s*(\S+)/)?.[1] || '';

  // Publication info
  const collection = body.match(/专辑名称[：:]\s*(.+?)(?=\n)/)?.[1] || '';
  const paperCount = body.match(/出版文献量[：:]\s*(.+?)(?=\n)/)?.[1] || '';

  // Evaluation info
  const impactComposite = body.match(/复合影响因子[：:]\s*([\d.]+)/)?.[1] || '';
  const impactComprehensive = body.match(/综合影响因子[：:]\s*([\d.]+)/)?.[1] || '';

  // "该刊被以下数据库收录" section - click "更多介绍" first if needed
  const moreBtn = Array.from(document.querySelectorAll('a')).find(a => a.innerText?.includes('更多介绍'));
  const hasMoreIntro = !!moreBtn;

  return {
    nameCN,
    nameEN,
    indexedIn,
    sponsor,
    frequency,
    issn,
    cn,
    collection,
    paperCount,
    impactComposite,
    impactComprehensive,
    hasMoreIntro,
    rawTagText: tagText.substring(0, 200)
  };
}
```

### 4. Get detailed indexing info (optional)

If the extraction shows `hasMoreIntro: true`, click the "更多介绍" link to expand detailed indexing information, then take a new snapshot to capture the expanded content.

The expanded section typically lists specific database inclusions with years, such as:
- 北大核心期刊（2023年版）
- CSCD中国科学引文数据库来源期刊（2023-2024年度）
- EI 工程索引（美）

### 5. Check "统计与评价" tab (for detailed metrics)

If the user wants detailed evaluation data:
- Find and click the "统计与评价" link/tab in the snapshot
- Wait for the statistics section to load
- Extract additional metrics (H-index, citation distribution, etc.)

### 6. Present results

```
## {nameCN} ({nameEN})

**收录数据库：** {indexedIn joined by " | "}

**基本信息：**
- ISSN: {issn}
- CN: {cn}
- 主办单位: {sponsor}
- 出版周期: {frequency}
- 专辑: {collection}
- 出版文献量: {paperCount}

**评价指标：**
- 复合影响因子 (2025版): {impactComposite}
- 综合影响因子 (2025版): {impactComprehensive}

**收录情况：**
{For each tag in indexedIn: "- ✓ {tag}"}
```

## Verified Page Structure

The journal detail page (`navi.cnki.net/knavi/detail`) has:

| Data                  | Location                                    |
|-----------------------|---------------------------------------------|
| Title                 | `h3.titbox.titbox1` — first line CN, second line EN |
| Indexing tags         | Text nodes after title: "北大核心", "EI", "CSCD", etc. |
| "被以下数据库收录"    | `h4` heading, below tags                   |
| Basic info            | Text patterns: "主办单位：", "ISSN：", "CN：", "出版周期：" |
| Publication info      | Text patterns: "专辑名称：", "出版文献量：" |
| Evaluation info       | Text patterns: "复合影响因子：", "综合影响因子：" |
| Detailed indexing     | Expandable via "更多介绍" link              |
| Stats tab             | "统计与评价" tab link                       |
| Detail page opens in  | **New tab** — use list_pages + select_page  |

## Common Indexing Databases

| Tag       | Full Name                                    |
|-----------|----------------------------------------------|
| 北大核心   | 北京大学中文核心期刊                          |
| CSSCI     | 中文社会科学引文索引                          |
| CSCD      | 中国科学引文数据库                            |
| SCI       | Science Citation Index                       |
| EI        | Engineering Index                            |
| CAS       | Chemical Abstracts Service                   |
| JST       | Japan Science and Technology Agency          |
| WJCI      | World Journal Clout Index                    |
| AMI       | 中国人文社会科学期刊 AMI 综合评价             |
| Scopus    | Elsevier Scopus                              |
