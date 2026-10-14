# AcadeMill-Econ — 项目执行说明

经管科研六模块工作流。保留原六个规范、`paper_assist_workflow.md`、`CLAUDE.md` 与 `.claude/`；Codex 扩展规则在本文件、项目技能和 docs 中维护。

## 路由

| 请求 | 技能 | 规范或参考 |
| --- | --- | --- |
| 泛读、批量泛读、精读、对比 | paper-reader | paper_reading_skills.md |
| 研究空白、挖掘缺口、评估选题、趋势分析、拓展选题、复制拓展、打磨选题、论证意义 | topic-selection | topic_selection_skills.md |
| 识别方案、设计参考、内生性诊断、稳健性清单 | research-design | research_design_skills.md |
| 数据推荐、变量构造、描述统计、回归代码 | data-empirical | data_empirical_skills.md |
| 文献综述、引言、摘要、背景理论、结果、结论、润色、审稿、回应、开题 | paper-writing | paper_writing_skills.md |
| 幻灯、讲稿、答辩问答、海报 | academic-presentation | academic_presentation_skills.md |
| 检索并阅读、下载并归档、Zotero归档、矩阵、文献库问答 | paper-researcher | 对应技能 |
| 补充缺失文献、补检索、补引用 | literature-supplement | 对应技能 |
| 中文文献、知网 | cnki-researcher | 对应技能 |
| 英文文献、Web of Science、WoS | wos-researcher | 对应技能 |
| 明确需要 Google Scholar | gs-researcher | 对应技能 |

技能位于 `.agents/skills/`，按需读取参考，无需启动子代理。旧 Task/agent 名称表达职责，不是强制调用。用户指令及已明确的持续授权优先。

## 材料与记录

研究讨论先读取 `research/AGENTS.md`，确定归属并建立本轮记录；每次实质进展保存需求、摘要、成果和下一步。维护、环境检查和一般问答不自动创建研究，不按 IDE 当前文件猜测归属。

研究目录 `research/R编号_名称/` 包含 `inbox/` 输入、`work/` 中间材料、`output/` 成果、`runs/` 记录。根 `inbox/` 只处理用户指定材料；根 `work/`、`output/` 用于维护或兼容，不混放研究。目录隔离不是权限隔离。

PDF 阅读和归档即使从根开始也须读 `paper-reading/AGENTS.md`。Python 3.10+，确认可用解释器，按需安装 requirements 依赖；PDF 提取器不含 OCR。

## 检索与归档

先读 `docs/LITERATURE_SEARCH.md`。默认校园示例为 Edge → 浙大 WebVPN → 人工登录 → 电子资源导航 → CNKI / WoS，其他学校或直接校园网按用户指定。有效登录复用受控会话，保留实际代理链接，不猜测加密路径或改用公网入口。

以实际工具和参数为准。示例 `cnki-browser` 控制 Edge，可用于 WoS，不虚构 `wos-browser`；明确 Scholar 请求才用 `gs-browser` 的 Chrome。独立配置，不运行原 `tools/switch-browser.ps1`。选择器只作参考，核对当前页面；只有可见验证码才交用户，不能据隐藏文字误报。付费逐篇确认。替代全文使用出版社、作者主页、机构仓储等合法来源。

Zotero 按 `docs/LITERATURE_WORKFLOW.md`：新使用者未启用持续授权时只做当次明确动作；启用后新选定文献下载完成默认查重归档并泛读。当次仅下载、不写库、不阅读优先；纯检索不自动下载或写库，不扫描旧目录。精读由用户指定。写前查重，写后读回父子关系，无权限时保存本地成果并标待归档。

密钥仅从进程环境或既有本机配置读取，不输出或保存到项目与日志。偏好可记于被忽略的 `LOCAL_PREFERENCES.md`，不得含密码、密钥或 Cookie。归档工具默认只读计划，`--apply` 仅用于已授权的具体批次。

## 证据与执行边界

不编造文献、DOI、数据、系数、显著性或页码。区分原文、用户输入、模型判断和待核验；无全文仅摘要分析。综述与空白使用矩阵和证据表，库中缺失不代表领域空白，未经外部核验不声称首次；AI 阅读不等于用户已读。

保留修改日志、仅必要修改与审稿仅报错约定。代码不等于已运行实证；未拒绝平行趋势差异不等于证明假设成立。导出 Word/PPT/PDF 依据实际工具，不能把文本或源码称为已导出。外部 skill/MCP 名称不是已安装能力。

## 开发与发布

先明确范围，保留原规范和 Claude 入口。运行相称的离线检查，不为验收写真实 Zotero、付费下载或改全局设置。状态见 `docs/VALIDATION.md`。

不得提交私人研究材料、下载文献、密钥、机器配置或浏览器数据；检查 `.gitignore` 与待发布文件。仅在用户请求发布或更新仓库时提交/推送指定范围，不覆盖其他分支或目录。
