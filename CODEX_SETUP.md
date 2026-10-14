# Codex 使用与可选连接

从仓库根目录启动，先完成 [README](README.md) 中的 Python 安装。本地阅读、选题、写作不要求校园或 Zotero 连接。

## 启动

安装并登录官方 Codex CLI 或 IDE 扩展，在根目录运行 `codex` 或用 IDE 打开仓库。让 agent“读取 AGENTS.md，核对技能和工具，只做检查”。技能在 `.agents/skills/`，引用同仓库规范与 docs；不只复制单个技能而丢失相对引用。结构与加载方式参考 [OpenAI Skills 文档](https://developers.openai.com/codex/skills/)。研究建立与恢复见 [研究指南](docs/RESEARCH_GUIDE.md)。

## 浏览器 MCP（可选）

可使用 [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)，另行安装并核对该版本 CLI 帮助。Edge 与 Chrome 使用独立数据目录，在本机填写实际可执行路径，不复用日常浏览器配置。

仓库只提供 [.codex/config.example.toml](.codex/config.example.toml)，路径为明确占位符。填好后复制为被 Git 忽略的 `.codex/config.toml`，只保留需要的服务，按 Codex 项目信任提示加载，不覆盖用户已有配置。配置语法与环境变量参考 [OpenAI MCP 文档](https://developers.openai.com/codex/mcp/)。

`cnki-browser` 为 Edge，用于校园 CNKI/WoS；`gs-browser` 为 Chrome，仅在明确需要 Scholar 时使用。浏览器数据目录放仓库外。首次检索在受控窗口人工登录，见 [校园路径](docs/LITERATURE_SEARCH.md)。不运行旧 `tools/switch-browser.ps1`。

## Zotero（可选）

可以使用当前 ChatGPT/Codex 的 Zotero 工具；克隆仓库不会安装 ChatGPT 插件，也不能保证不同插件方法相同。核对实际工具、库、合集、全文覆盖和写权限。本地 API 模式先启动 Zotero Desktop，按已安装集成的说明启用访问。

stdio MCP 可参考 [zotero-mcp](https://github.com/54yyyu/zotero-mcp)，安装和参数以该集成文档为准。示例配置采用本地读取模式；可读不代表可写。Better BibTeX 只用于其特定引用键等功能，不是笔记或 Web API 写入的前提。

`tools/zotero_archive.py` 通过 Pyzotero Web API 归档已核实的书目、PDF、笔记、证据，不生成阅读内容。安装 `requirements-zotero.txt`；凭据来自进程 `ZOTERO_API_KEY`、`ZOTERO_LIBRARY_ID`、`ZOTERO_LIBRARY_TYPE=user`，或既有本机 `.claude.json` 中唯一匹配的 Zotero 个人库。密钥不得写入项目或聊天；该工具不处理群组库。

已配置唯一 Zotero 凭据且需要传给子进程时，Windows 可用：

```powershell
./tools/start-codex.ps1 -Mode cli
# IDE 模式先结束旧 VS Code 进程，确保环境继承
./tools/start-codex.ps1 -Mode vscode
```

启动器只临时传递进程环境，退出恢复，不改全局设置或打印密钥。没有凭据时直接启动 Codex，继续本地工作并标待归档。归档清单与计划命令见 [Zotero 执行规则](.agents/skills/paper-researcher/references/zotero-workflow.md)。

## 首次核对

- 本地离线测试与 PDF 文本提取。
- 校园实际导航与机构权限；认证人工处理，额外付费不自动执行。
- Zotero 先只读查库/查重，再做明确授权的单篇归档，读回父项、附件、笔记；云端核验与桌面同步分别记录。

安装验收不自动写真实库，当前状态见 [VALIDATION.md](docs/VALIDATION.md)。
