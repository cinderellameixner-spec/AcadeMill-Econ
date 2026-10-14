# 目录地图

```text
AcadeMill-Econ/
├─ AGENTS.md                项目执行规则与路由
├─ CLAUDE.md、.claude/       原 Claude 兼容入口
├─ *_skills.md              原六模块规范
├─ paper_assist_workflow.md  原全局关系
├─ .agents/skills/          Codex技能与按需参考
├─ .codex/config.example.toml  可选配置示例，不是实际配置
├─ docs/                    使用说明、验证状态与变更记录
├─ paper-reading/           原阅读规则与Codex扩展规则
├─ research/AGENTS.md       研究保存与恢复规则
├─ tools/                   PDF提取、研究目录、证据状态、Zotero归档
├─ tests/                   临时材料与模拟客户端的离线测试
└─ requirements*.txt        基础及可选依赖
```

运行时创建的 `research/R编号_名称/` 含 inbox/work/output/runs、PROJECT.md、sources.md、decisions.md。根 inbox/work/output 按需创建；不随仓库分发。实际研究、配置、浏览器数据和密钥默认不提交。

技能引用规范与docs，保留完整仓库以保证相对链接。`references/` 是按需模板，不等于外部工具已安装。规范的旧平台路径由当前执行规则与实际工具覆盖；原Claude配置含历史机器路径，使用者须按本机核对，Codex不运行旧切换脚本。

使用入口见 [README](../README.md)，能力边界见 [VALIDATION](VALIDATION.md)。
