# Codex 文献阅读与归档

根目录 `AGENTS.md` 的路由和事实约束适用。阅读模板用 `paper-reader` 技能；规范见 `../paper_reading_skills.md`。
本文件替代旧 `CLAUDE.md` 中 Claude CLI 安装/注册步骤，不运行旧安装指令。

1. 用户 PDF 从项目 `inbox/` 读取；原 `tools/extract_pdf.py` 可提取文本。扫描 PDF 的空文本需要 OCR，目前未实现。
2. 有检索需求时按 `paper-researcher` 流程与 `../docs/LITERATURE_SEARCH.md`，默认在同一 Edge 会话打开浙大 WebVPN，人工登录后从电子资源导航进入中文 CNKI / 英文 Web of Science。已登录时复用会话。仅明确需要 Google Scholar 时才走 Chrome；按用户指定使用 Scholar 路径。
3. 归档前按 DOI/标题查重，确定文献父条目；创建条目、附件、笔记后读回验证。
4. 阅读模式为泛读、精读；对比是综合操作。遵循 ../docs/LITERATURE_WORKFLOW.md 和 ../.agents/skills/paper-researcher/references/zotero-workflow.md。笔记先保存本地Markdown，再写文献父条目下的HTML note，标题含模式、日期、版本，公式保留原文；先查已有笔记，同内容复用，变化另存版本，不覆盖人工笔记。
5. 对比笔记在参与比较的各父条目下关联；记录归档成功、失败与未完成项。
6. Zotero MCP 可读不代表可写；核对当前工具和凭据。若写入失败，保存正文到 `output/` 供恢复，不声称已归档。
7. 优先使用当前GPT/Codex的实际Zotero工具导入本地PDF或书目；已有条目只补缺失部分。没有补附件工具时标待补，不创建重复父条目。旧Connector脚本仅作已核兼容的备选，409不代表成功。inbox/.attach_pdf.py是旧会话脚本，不能当通用附件工具。
8. 仅在用户已启用协同时，下载后默认查重、归档和泛读；否则只执行当次明确授权动作。纯检索不写库，明确仅下载/不归档/不阅读时遵循当次指令。凭据仅在本机内存读取，不保存密钥。归档、附件、阅读、笔记状态分别保存并读回核对，实际验收见 `../docs/VALIDATION.md`。
