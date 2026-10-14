---
name: paper-researcher
description: 串联校园文献检索、下载、Zotero归档、泛读或精读、文献矩阵与文献库问答，并衔接综述、研究空白和补文献。
---

# 检索工作流

先读 [校园文献检索路径](../../../docs/LITERATURE_SEARCH.md)，再按 [工作流参考](references/workflow.md) 执行当前请求。
涉及归档或阅读时读取 [Zotero执行规则](references/zotero-workflow.md)；涉及矩阵、综述、空白或补文献时读取 [证据与成果契约](references/evidence-contract.md)。使用方式与默认授权见 [文献协同指南](../../../docs/LITERATURE_WORKFLOW.md)。纯库内操作不打开校园浏览器。

## Codex 执行约定

以当前可用工具为准：文档里的 MCP 工具名是能力提示，先核对真实工具名称、参数和返回结果。工具缺失就报告缺失，不声称已检索、归档或生成文件。
按本次任务读取所需参考段落，不要一次加载全部模块。用户级 Claude 配置只作迁移来源，不在新项目中修改。
中文触发词直接路由；原先的 Task/agent 调用表示工作流职责，不意味着必须创建子代理。
不编造文献、DOI、系数、样本量或显著性；事实与推测分开，数据缺失时标明待补。
Word、PowerPoint、PDF 成稿按当前环境实际可用的文档/演示/PDF技能交付；找不到工具时提供明确的文本或源码产物，不能把大纲称为已生成的文件。旧文档中的 anthropics/skills 等为可选旧集成，不自动安装。

默认中文用 CNKI，英文用 `wos-researcher` / Web of Science，中英文用两者。统一通过 `cnki-browser` 控制 Microsoft Edge：打开浙大 WebVPN，等待用户手动登录，再从电子资源导航点击数据库入口；有效登录复用同一会话，保留代理链接。仅明确需要 Google Scholar 时才调用已有 `gs-*` / Chrome，本规则优先于旧公网 URL 和浏览器描述。
先核对实际可用的检索技能与 MCP。没有全文的论文只能按摘要分析并注明，不输出伪造的精读内容。
原流程中逐步确认按用户当前授权处理；已明确授权的免费检索和归档继续执行，付费下载逐篇确认，验证码交用户处理。
归档前查重，写入后读取确认。Connector 的 409 只代表旧会话冲突，不能单凭它认定条目或附件已成功入库。
