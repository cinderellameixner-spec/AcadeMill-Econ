# paper assist — 科研工作流 Agent

这是一个面向**经济学与管理学研究者**的一体化科研 agent。目标是把科研流程中重复性高、结构化强的环节自动化，让研究者专注于真正需要创造力的部分。项目按 6 个模块规划（详见 §0），**当前文献阅读模块已完成，其余模块开发 / 规划中**。

已完成的文献阅读模块核心能力：

1. **三种阅读模式** — 泛读（批量速览）/ 精读（五模块深读）/ 对比（多文献横向比较）。
2. **结构化笔记** — 严格遵循 [paper_reading_skills.md](paper_reading_skills.md) 的写作规范输出中文阅读笔记。
3. **自动归档到 Zotero** — 每篇文献以「父条目 + PDF 附件 + 阅读笔记子条目」的三层结构入库。

---

## 0. 全局工作流与模块路线图（指针，不复述）

> 项目级架构、6 模块详细说明、模块协作关系、开发规范的**权威源**是 [paper_assist_workflow.md](paper_assist_workflow.md)。本节只保留高频速查信息，细节一律以该文档为准，避免双源漂移。

### 0.1 项目定位

- **服务对象：** 经管类硕博研究生、青年学者、高校教师，具备基本计量训练与文献检索能力。
- **核心理念：** 每个模块独立可用、可自由组合；箭头是建议路径，不是强制顺序。用户可从任一模块切入，不必走完整链路。
- **工作流全景：** 探索阶段（文献阅读 ⇄ 选题辅助）→ 建构阶段（研究设计 → 数据与实证）→ 产出阶段（论文写作 → 学术报告）。完整全景图见 [paper_assist_workflow.md](paper_assist_workflow.md) §「科研工作流全景」。

### 0.2 模块总览

| 序号 | 模块 | 状态 | Skill 文件 | 核心指令 |
| - | - | - | - | - |
| 1 | 文献阅读 | ✅ 已完成 | paper_reading_skills.md | 泛读、精读、对比 |
| 2 | 选题辅助 | 🔧 开发中 | topic_selection_skills.md | 挖掘缺口、评估选题、趋势分析、拓展选题、复制拓展、打磨选题、论证意义 |
| 3 | 研究设计 | 📋 规划中 | — | — |
| 4 | 数据与实证 | 📋 规划中 | — | — |
| 5 | 论文写作 | 📋 规划中 | — | — |
| 6 | 学术报告 | 📋 规划中 | — | — |

模块职责、上下游数据流、阅读 ⇄ 选题 的三种使用路径（先读后选 / 先选后读 / 交替迭代）详见 [paper_assist_workflow.md](paper_assist_workflow.md)。

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
| 研究设计 / 数据与实证 / 论文写作 / 学术报告 | 规划中 | — | 触发词待定 |

> 文献阅读模块的**操作级分派**（含 PDF 上传、检索+阅读自然语言）见下方 §1。

### 0.4 开发规范（要点）

- 新增模块：先在 [paper_assist_workflow.md](paper_assist_workflow.md) 补模块说明 → 建独立 skill 文件（只含角色定义、风格规范、指令模板）→ 更新本文件 §0.2 总览表与 §0.3 路由表 → **不改动已完成模块的 skill 与代码** → 完成后 git commit（"完成 [模块名称] 模块"）。
- 全局背景（定位、模块关系等）写进 workflow 文档，不放进 skill 文件；skill 文件只放执行任务所需内容。
- 各模块写作风格规范（术语处理、引用格式、可视化）保持一致；每个指令唯一中文触发词、互不歧义。

---

## 1. 触发词与默认行为

所有阅读任务**统一调用 `paper-reader` skill**，根据触发词分派模式：

| 用户输入 | 行为 |
|---|---|
| 「泛读 …」/「批量泛读 …」 | `paper-reader` 泛读模式（输出 12 字段表格） |
| 「精读 …」 | `paper-reader` 精读模式（五模块：标题摘要 / 引言 / 方法 / 结果 / 结论） |
| 「对比 …」+ 两篇及以上 | `paper-reader` 对比模式（13 维 Markdown 表格 + 研究脉络分析） |
| 上传 PDF / 给出 PDF 路径 | 走 §3「PDF 归档流程」 |
| 「检索 + 阅读」类自然语言（如「找 5 篇近 2 年数字经济 CSSCI 论文然后精读」） | 调用 `paper-researcher` agent 串联检索 → 下载 → Zotero → 阅读 |

阅读完成后，笔记**必须**按 §3 流程写回 Zotero，不要只在对话中输出。

---

## 2. 阅读规范（指针，不复述）

写作风格、术语处理、公式呈现、数据标注、APA 引用：**全部遵循 [paper_reading_skills.md](paper_reading_skills.md)**。

三种模式的具体输出模板（泛读字段表、精读五模块结构、对比 13 维表）以 `~/.claude/skills/paper-reader/SKILL.md` 为可执行版本，本文件不再重复模板，避免双源漂移。

---

## 3. PDF → Zotero → 笔记 归档流程

### 3.1 两条入口

- **入口 A — 手动上传**：用户将 PDF 放入 `d:\MyDesktop\cc.project\paper assist\inbox\`（首次使用时自行创建该目录）或直接给出 PDF 路径，agent 接管归档。
- **入口 B — 自动检索**：通过 `paper-researcher` agent 完成 CNKI / Google Scholar 检索下载后，产物已落到 Zotero，本流程接管笔记生成。

两条入口最终汇入同一个 Zotero 归档结构。

### 3.2 Zotero 中的目标结构

```
📁 父条目【文献标题】(item type: journalArticle / book 等)
   ├── 📎 PDF 附件（原始 PDF）
   └── 📝 子笔记（item type: note）—— 阅读笔记
        类型由触发指令决定：泛读笔记 / 精读笔记 / 对比笔记
```

笔记形式固定为 **Zotero 内置笔记（note 子条目，富文本）**，**不要**落地为 .md 附件。

### 3.3 标准操作步骤

1. **PDF 入库为父条目**（按优先级尝试）：
   1. PDF 含可解析元数据 / DOI → `zotero_add_by_doi`。
   2. 来源是 CNKI / Google Scholar → 复用 `~/.claude/skills/cnki-export/scripts/push_to_zotero.py` 或 `~/.claude/skills/gs-export/scripts/push_to_zotero.py`（详见 `~/.claude/agents/paper-researcher.md` §4）。
   3. 兜底：直接通过 Zotero MCP 创建 item 并 attach PDF。
   - **入库前先 `zotero_search_items` 查重**，避免重复条目。

2. **生成笔记内容**：
   - 用 `zotero_get_item_fulltext` 取全文（必要时配合 `zotero_get_annotations` 读已有批注）。
   - 调用 `paper-reader` skill 按对应模式输出笔记。

3. **写回为 note 子条目**：
   - 用 `zotero_create_note(item_key=<父条目 key>, note_title=..., note_text=...)` 在父条目下创建 note 子项（`item_key` 必须是文献父条目，不是 PDF 附件）。
   - 笔记标题统一格式：`{泛读笔记|精读笔记|对比笔记} — YYYY-MM-DD`。
   - **HTML 富文本**：笔记正文必须用 HTML（`<h1>/<h2>/<h3>`、`<ul>/<li>`、`<strong>`、`<blockquote>`、`<table>` 等），不能只贴 Markdown 原文（`#`/`**`/`-` 会在 Zotero 中原样显示、无层级）。Zotero note 不支持自定义 class/style；公式用 `$...$` / `$$...$$` 包裹保留原文。
   - **分点另起一行**：同一标题下的多个分点/小点必须各自另起一行（独立 `<li>` 或 `<p>`），禁止用顿号/分号把多个并列要点压在同一行，以提高可读性。
   - **写入失败处理**：若 `zotero_create_note` 报 `Cannot perform write operations in local-only mode`，说明 MCP 仍是 local-only 模式（缺 `ZOTERO_API_KEY` / `ZOTERO_LIBRARY_ID`）——按 §4 配置 hybrid 模式后才能写笔记；在配好之前不要默默放弃，把笔记内容回贴给用户备份。
   - **挂载校验**：创建后用 `zotero_get_item_children(item_key=<父条目 key>)` 确认该 note 作为子项出现（防止退化成 standalone note）。

4. **对比模式特殊处理**：
   - 对比涉及 N 篇文献时，**默认在每篇父条目下各挂一份相同的对比 note**，保证从单篇视角也能看到对比结论。
   - 不要只在某一篇下挂笔记，也不要只生成一个独立 standalone note。

---

## 4. Zotero MCP 自检与安装

### 4.1 自检（每次会话首次调用 zotero_* 时）

先确认 MCP 工具可用：列出当前 MCP 工具，确认 `zotero_search_items` / `zotero_get_item_fulltext` / `zotero_add_by_doi` 等是否存在。

- ✅ 存在 → 直接进入 §3 归档流程。
- ❌ 不存在 → 暂停，按 §4.2 提示用户安装。

**写入能力（hybrid 模式）**：读操作走本地 API 即可，但**写笔记 / 建条目必须配 hybrid 模式**（`ZOTERO_LOCAL=true` + `ZOTERO_API_KEY` + `ZOTERO_LIBRARY_ID`）。只配 `ZOTERO_LOCAL=true` 的 local-only 模式下，`zotero_create_note` 等写操作会直接报 `Cannot perform write operations in local-only mode`（Zotero 桌面端本地 API 只读，无纯本地写入路径）。首次遇到该报错 → 按 §4.2 配置 hybrid。

### 4.2 安装指引（zotero-mcp）

参考开源实现：`https://github.com/54yyyu/zotero-mcp`（PyPI 包名 `zotero-mcp-server`）。

前置条件：
- Zotero 7+ 桌面端已启动；
- 在 `编辑 → 首选项 → 高级 → 允许其他应用程序与 Zotero 通信` 中开启本地 API（默认端口 23119）；
- **写笔记必须开启 Zotero 同步**（`编辑 → 首选项 → 同步`，登录账号）——hybrid 模式的写入先到云端再同步回落本地。

**安装**（任选其一）：
- `uv tool install zotero-mcp-server`（推荐，需先装 uv）
- `pipx install zotero-mcp-server`
- `pip install zotero-mcp-server`（用现成 Python 环境）

**获取 Web API 凭据**（hybrid 写入必需）：
- API key：访问 `https://www.zotero.org/settings/keys/new`，勾选 **Allow write access**，创建后复制 key。
- Library ID：在 `https://www.zotero.org/settings/keys` 页面顶部「Your userID for use in API calls is **XXXXXXX**」即数字 library id（个人库）。群组库则用群组数字 ID，并额外设 `ZOTERO_LIBRARY_TYPE=group`（个人库默认 `user`，无需设置）。

**注册到 Claude Code**（不要直接编辑 `settings.json` 的 `mcpServers` 字段 —— 当前 schema 不接受该字段；MCP server 实际存放在 `~/.claude.json`）。统一通过 CLI 注册为 **hybrid 模式**：

```powershell
claude mcp add zotero -s user `
  -e ZOTERO_LOCAL=true `
  -e ZOTERO_API_KEY=<带写权限的 key> `
  -e ZOTERO_LIBRARY_ID=<数字 library id> `
  -e PYTHONIOENCODING=utf-8 `
  -- "<zotero-mcp.exe 绝对路径>" serve
```

- `-s user`：写入用户级配置（跨项目可用）。
- `ZOTERO_LOCAL=true`：读仍走本地（全文/检索快、不耗 Web API 配额）；同时有 key+id 时自动进入 hybrid，写走 Zotero Web API。
- `ZOTERO_API_KEY` / `ZOTERO_LIBRARY_ID`：缺任一则退回 local-only，写操作不可用。key 是密钥，只进 `~/.claude.json`，不要写入会提交的文件。
- `PYTHONIOENCODING=utf-8`：避免 Windows GBK 控制台对 emoji 输出报错。
- 绝对路径示例：`D:\app\python3.11\Scripts\zotero-mcp.exe`（pip 安装在哪个 Python 下就在哪个 Scripts 目录）。
- 已注册过 zotero（如仅 local-only）需先 `claude mcp remove zotero -s user` 再按上方重注册。

**验收**：执行 `claude mcp list`，应看到 `zotero: ... ✓ Connected`；重启 Claude Code 后，`zotero_create_note` 不再报 local-only 错误，且 `zotero_get_item_children` 能看到新建笔记作为父条目子项。

---

## 5. 关联组件速查

| 用途 | 路径 |
|---|---|
| 阅读规范源（项目内） | [paper_reading_skills.md](paper_reading_skills.md) |
| 阅读执行 skill | `~/.claude/skills/paper-reader/SKILL.md` |
| 检索串联 agent | `~/.claude/agents/paper-researcher.md` |
| CNKI → Zotero 推送脚本 | `~/.claude/skills/cnki-export/scripts/push_to_zotero.py` |
| Google Scholar → Zotero 推送脚本 | `~/.claude/skills/gs-export/scripts/push_to_zotero.py` |

---

## 6. 行为约束

- 阅读笔记一律**中文**，遵循 `paper_reading_skills.md` 的客观克制风格；核心术语保留英文原文 + 中文译名（如 `instrumental variable（工具变量）`）。
- **不**在本文件或对话中重复 skill 已写明的模板/表格，避免双源漂移。
- Zotero 任何**写入**操作（建条目、挂笔记）前先 `zotero_search_items` 查重。
- **付费下载逐篇确认**：任何会触发扣费的付费下载，必须逐篇用 `AskUserQuestion` 确认，不能批量授权连续扣费。
- **CNKI 浏览器约束**：访问 / 下载 CNKI（知网）必须使用 **Edge 且不走代理**（Chrome 走代理打不开知网）；下载前需先登录 CNKI。
- 异常处理参考 `~/.claude/agents/paper-researcher.md` 的错误处理表：CNKI 滑块验证码 → 暂停等待人工；Zotero 未启动 → 提示用户启动；MCP 不可用 → 走 §4.2 安装流程。
