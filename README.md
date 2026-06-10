# paper assist

> ⚠️ 项目处于开发中（v0.x），核心 6 模块已可用，欢迎试用与反馈。

把经管类科研流程里重复、结构化的环节交给 Claude，让研究者专注思考。

## 这是什么

面向**经管类硕博研究生、青年学者与高校教师**的一体化科研 agent，覆盖从读文献到做答辩的完整链路。基于 Claude Code skills 构建，用一个中文触发词就能唤起对应能力——输入 PDF、研究问题或回归表，拿回笔记、识别方案、可跑代码与论文段落。

## 核心亮点

- **覆盖全流程**：从读文献到做答辩，6 个模块串起完整科研链路
- **模块独立 + 自由组合**：不强制顺序，可从任意模块切入
- **中文触发词**：所有指令一个词唤起（如「精读」「评估选题」「回归代码」）
- **接通 Zotero / CNKI / Google Scholar**：通过 MCP 直接检索、下载、归档
- **可执行产出**：给的是 Stata/Python 代码片段、Response Letter 草稿、Beamer 模板，不是空泛建议

## 六大模块

| 模块 | 状态 | 你输入 | 你拿到 |
| --- | --- | --- | --- |
| 1. 文献阅读 | ✅ | PDF / DOI / 检索词 | 泛读卡片、精读五模块笔记、多篇对比表，自动入 Zotero |
| 2. 选题辅助 | ✅ | 阅读笔记 / 模糊想法 | 研究缺口清单、六维可行性评分、复制拓展方向、打磨后的研究问题 |
| 3. 研究设计 | ✅ | 研究问题 + 数据条件 | 因果识别方案（DID/IV/RDD…）、3—5 篇参考文献、内生性诊断、稳健性清单 |
| 4. 数据与实证 | ✅ | 变量需求 | 数据源推荐、变量构造代码、描述统计模板、主回归 + 平行趋势 + 异质性 + 机制全套代码 |
| 5. 论文写作 | ✅ | 笔记 + 回归表 | 综述、引言、摘要、结果描述、结论、审稿模拟、Response Letter、开题报告 |
| 6. 学术报告 | ✅ | 论文初稿 | PPT/Beamer 幻灯、逐页讲稿、答辩问答预判、会议海报 |

> 状态图例：✅ 已完成 / 🔧 开发中 / 📋 规划中

## 快速开始

**环境要求**

- Claude Code（CLI 或 IDE 插件）
- Zotero 7 + Better BibTeX 插件（笔记归档）
- 浏览器：Edge 用于 CNKI（不走代理），Chrome 用于 Google Scholar
- Stata 17+ 或 Python 3.10+（运行实证代码）

**安装**

1. 克隆仓库到本地：

   ```bash
   git clone https://github.com/<your-name>/paper-assist.git
   ```

2. 把各模块 skill 目录拷贝或软链到 `~/.claude/skills/`，例如：

   ```bash
   # macOS / Linux
   ln -s "$PWD/skills/paper-reader" ~/.claude/skills/paper-reader
   ```

   ```powershell
   # Windows PowerShell（管理员）
   New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\paper-reader" -Target "$PWD\skills\paper-reader"
   ```

3. 配置 MCP：Zotero MCP、Chrome DevTools MCP（按各 skill 文档指引）。
4. 在 Claude Code 中打开项目根目录，`CLAUDE.md` 会自动加载，触发词随即可用。

**使用示例**

- `精读 P1` → 对 `inbox/` 里第 1 篇 PDF 做五模块精读
- `挖掘缺口` → 从 Zotero 笔记里识别可做选题
- `回归代码 我的设计是 DID，处理组是…` → 给一份可跑的 .do 文件
- `开题报告` → 整合前 4 个模块的产出，生成完整开题报告

完整触发词清单见 [CLAUDE.md](CLAUDE.md) §0.3，模块协作关系见 [paper_assist_workflow.md](paper_assist_workflow.md)。

## 当前开发进度

- ✅ 模块 1—6 已完成并通过实际项目验证
- 🔧 文档完善、安装脚本、示例数据集
- 📋 后续：可视化辅助、英文文献兼容、更多期刊投稿模板

## License

MIT — 见 [LICENSE](LICENSE)
