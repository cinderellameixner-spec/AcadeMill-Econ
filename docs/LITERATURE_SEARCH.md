# 校园资源文献检索路径

浙大为校园访问示例，其他学校可指定自己的 VPN、校园网或资源入口。仓库不保存使用者账号。

| 需求 | 入口 | 浏览器 |
| --- | --- | --- |
| 中文 | 浙大 WebVPN → 电子资源导航 → CNKI | Microsoft Edge |
| 英文 | 同一导航页 → Web of Science | 同一 Edge 会话 |
| 明确指定 Scholar | 单独配置的 Google Scholar 路径 | Google Chrome |

示例 MCP `cnki-browser` 是 Edge 能力，可控制 VPN、WoS 和出版社，不限于知网；实际工具名称与参数按会话核对。Chrome 的 `gs-browser` 使用独立配置，校园入口失败不自动转 Scholar。

## 人工登录与导航

1. 查看受控 Edge 标签；无有效会话时打开 [浙大 WebVPN](https://webvpn.zju.edu.cn/)，已有页面则复用。直接校园网访问按用户当次指定处理。
2. 用户在该窗口手动输入自己的账号、密码并完成认证，再告知“已登录，继续”。不索取或保存密码、动态口令和 Cookie。登录未完成暂停依赖操作，不持续刷新。
3. 确认后读实际页面，核对电子资源导航，点击可见 CNKI / WoS 入口。新开标签后核对导航来源、标题与页面内容。
4. 保留 WebVPN 代理地址，不猜测加密路径或换公网直链；会话失效或权限不足时报告真实状态并保留检索计划，不说成无文献。

## 检索与获取全文

- 中文使用 `cnki-researcher` 及按需 `cnki-*`；英文使用 `wos-researcher`。先核对当前界面，再设置字段、年份、刊名和类型。
- 记录检索式、数据库子库、日期、筛选、命中数及纳入/排除理由。核对筛选实际生效；仅填入年份不能作为已过滤的证据。
- 从详情页实际下载入口获取全文。WoS 可能转出版社或学校解析页，保留校园会话；有记录不等于有全文订阅。
- 校园权限内按授权下载，额外付费逐篇确认。验证码人工处理，但先核对截图/元素尺寸与位置：隐藏预加载组件文字不能作为验证码挑战证据。
- 检查实际文件、格式、页数与可打开性才标下载完成。无法取得全文时保留原因，可查出版社、作者主页或机构仓储等合法来源。
- PDF 放研究 `inbox/`，导出和缓存放 `work/`，结果与笔记放 `output/`；桌面等用户指定位置尊重并登记。

归档按 [文献协同指南](LITERATURE_WORKFLOW.md) 与授权，下载、附件写入、桌面同步分别验证。跨库按 DOI、题名、作者、年份查重，不自动合并不同版本。WoS 使用实际导出菜单，不复用 Scholar data-cid。无全文仅摘要级记录；研究归属见 [研究规则](../research/AGENTS.md)。

当前验收范围见 [VALIDATION.md](VALIDATION.md)。数据库页面和学校权限可能变化，使用时须核对。

参考：[浙大入口](https://webvpn.zju.edu.cn/)、[WoS 检索帮助](https://webofscience.help.clarivate.com/en-us/Content/document-search.htm)、[全文选项](https://webofscience.help.clarivate.com/en-us/Content/wos-core-collection/wos-full-record.htm)。
