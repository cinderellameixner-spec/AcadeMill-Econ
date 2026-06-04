# paper assist — 科研工作流 Agent

这是一个面向**经济学与管理学研究者**的一体化科研 agent。目标是把科研流程中重复性高、结构化强的环节自动化，让研究者专注于真正需要创造力的部分。项目按 6 个模块规划（详见 §0），**当前文献阅读、选题辅助、研究设计、数据与实证、论文写作模块已完成，学术报告模块规划中**。

各模块的执行细则由各自的子 CLAUDE.md 与 skill 文件承载，本文件只承担**全局路由**职责：项目定位、模块总览、触发词分派、开发规范。

---

## 0. 全局工作流与模块路线图（指针，不复述）

> 项目级架构、6 模块详细说明、模块协作关系、开发规范的**权威源**是 [paper_assist_workflow.md](paper_assist_workflow.md)。本节只保留高频速查信息，细节一律以该文档为准，避免双源漂移。

### 0.1 项目定位

- **服务对象：** 经管类硕博研究生、青年学者、高校教师，具备基本计量训练与文献检索能力。
- **核心理念：** 每个模块独立可用、可自由组合；箭头是建议路径，不是强制顺序。用户可从任一模块切入，不必走完整链路。
- **工作流全景：** 探索阶段（文献阅读 ⇄ 选题辅助）→ 建构阶段（研究设计 → 数据与实证）→ 产出阶段（论文写作 → 学术报告）。完整全景图见 [paper_assist_workflow.md](paper_assist_workflow.md) §「科研工作流全景」。

### 0.2 模块总览

| 序号 | 模块 | 状态 | 模块细则 / Skill 文件 | 核心指令 |
| - | - | - | - | - |
| 1 | 文献阅读 | ✅ 已完成 | [paper-reading/CLAUDE.md](paper-reading/CLAUDE.md) / paper_reading_skills.md（规范） / `~/.claude/skills/paper-reader/SKILL.md`（执行） | 泛读、精读、对比 |
| 2 | 选题辅助 | ✅ 已完成 | topic_selection_skills.md（规范） / `~/.claude/skills/topic-selection/SKILL.md`（执行） | 挖掘缺口、评估选题、趋势分析、拓展选题、复制拓展、打磨选题、论证意义 |
| 3 | 研究设计 | ✅ 已完成 | research_design_skills.md（规范） / `~/.claude/skills/research-design/SKILL.md`（执行） | 识别方案、设计参考、内生性诊断、稳健性清单 |
| 4 | 数据与实证 | ✅ 已完成 | data_empirical_skills.md（规范） / `~/.claude/skills/data-empirical/SKILL.md`（执行） | 数据推荐、变量构造、描述统计、回归代码 |
| 5 | 论文写作 | ✅ 已完成 | paper_writing_skills.md（规范） / `~/.claude/skills/paper-writing/SKILL.md`（执行） | 综述生成、引言起草、摘要生成、背景理论、结果描述、结论撰写、表达润色、审稿模拟、回应审稿、开题报告 |
| 6 | 学术报告 | 📋 规划中 | — | — |

模块职责、上下游数据流、阅读 ⇄ 选题 的三种使用路径（先读后选 / 先选后读 / 交替迭代）、选题辅助模块「解决什么问题」与「七指令组合路径 A/B/C/D」均详见 [paper_assist_workflow.md](paper_assist_workflow.md)。

### 0.3 触发词路由总表（全量；操作细则见各模块章节）

| 触发词 | 所属模块 | Skill 文件 | 功能简述 |
| - | - | - | - |
| 泛读 / 批量泛读 | 文献阅读 | paper_reading_skills.md | 快速提取文献核心要素 |
| 精读 | 文献阅读 | paper_reading_skills.md | 五模块深入分析 |
| 对比 | 文献阅读 | paper_reading_skills.md | 多篇文献横向对比表 |
| 挖掘缺口 | 选题辅助 | topic_selection_skills.md | 从笔记中识别研究缺口 |
| 评估选题 | 选题辅助 | topic_selection_skills.md | 六维可行性评估 |
| 趋势分析 | 选题辅助 | topic_selection_skills.md | 研究方向趋势与竞争态势 |
| 拓展选题 | 选题辅助 | topic_selection_skills.md | 交叉方向发散 |
| 复制拓展 | 选题辅助 | topic_selection_skills.md | 基于标杆论文生成方向 |
| 打磨选题 | 选题辅助 | topic_selection_skills.md | 结构化追问聚焦问题 |
| 论证意义 | 选题辅助 | topic_selection_skills.md | 生成现实意义论证素材 |
| 识别方案 | 研究设计 | research_design_skills.md | 可执行的因果识别方案（处理组定义/模型设定/检验设计） |
| 设计参考 | 研究设计 | research_design_skills.md | 3—5 篇类似设计的已发表文献对比 |
| 内生性诊断 | 研究设计 | research_design_skills.md | 五类内生性来源系统排查 + 应对方案 |
| 稳健性清单 | 研究设计 | research_design_skills.md | 按主回归生成五大类稳健性检验清单 |
| 数据推荐 | 数据与实证 | data_empirical_skills.md | 数据需求拆解 + 数据源推荐 + 替代路径 + 多源匹配方案 |
| 变量构造 | 数据与实证 | data_empirical_skills.md | 核心变量操作性定义 + Stata/Python 构造代码 + 常见坑预警 |
| 描述统计 | 数据与实证 | data_empirical_skills.md | 描述统计表 / 相关矩阵 / 分组均值差异 / 分布检查代码模板 |
| 回归代码 | 数据与实证 | data_empirical_skills.md | 主回归 + 平行趋势 + 稳健性 + 异质性 + 机制检验代码框架 |
| 综述生成 | 论文写作 | paper_writing_skills.md | 基于 Zotero 笔记 + 对比表生成文献综述初稿 |
| 引言起草 | 论文写作 | paper_writing_skills.md | 五段式引言（背景/缺口/做法/发现/贡献），复用【论证意义】【挖掘缺口】 |
| 摘要生成 | 论文写作 | paper_writing_skills.md | 中英文摘要 + 关键词 + JEL Classification |
| 背景理论 | 论文写作 | paper_writing_skills.md | 制度背景梳理 + 理论机制推导 + H1—H3 假设 |
| 结果描述 | 论文写作 | paper_writing_skills.md | 回归表 → 规范结果描述段落（主回归/稳健性/异质性/机制） |
| 结论撰写 | 论文写作 | paper_writing_skills.md | 四段式结论（发现/启示/局限/未来）+ 与引言呼应检查 |
| 表达润色 | 论文写作 | paper_writing_skills.md | 中/英文学术润色 + 修改日志 + 阈值原则 |
| 审稿模拟 | 论文写作 | paper_writing_skills.md | Reviewer 视角意见稿，致命/小问题分级（仅报错） |
| 回应审稿 | 论文写作 | paper_writing_skills.md | 逐条拆解 referee report → Response Letter 框架 |
| 开题报告 | 论文写作 | paper_writing_skills.md | 整合模块 1—4 全部产出 → 完整开题报告 |
| 学术报告 | 规划中 | — | 触发词待定 |

> 文献阅读模块的**操作级分派**（含 PDF 上传、检索+阅读自然语言、Zotero 归档流程、MCP 自检安装、行为约束等）见 [paper-reading/CLAUDE.md](paper-reading/CLAUDE.md)。

### 0.4 开发规范（要点）

- 新增模块：先在 [paper_assist_workflow.md](paper_assist_workflow.md) 补模块说明 → 建独立 skill 文件（只含角色定义、风格规范、指令模板）→ 更新本文件 §0.2 总览表与 §0.3 路由表 → **不改动已完成模块的 skill 与代码** → 完成后 git commit（"完成 [模块名称] 模块"）。
- 全局背景（定位、模块关系等）写进 workflow 文档，不放进 skill 文件；skill 文件只放执行任务所需内容。
- 各模块写作风格规范（术语处理、引用格式、可视化）保持一致；每个指令唯一中文触发词、互不歧义。
