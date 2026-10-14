---
name: gs-export
description: 从明确指定的Google Scholar论文导出引用或BibTeX，并按授权查重归档到Zotero。
---

# Scholar 引用导出

仅明确Google Scholar需求时使用Chrome与当前实际 `gs-browser` 工具。先检查当前页面；不要将Scholar选择器套用于CNKI/WoS。

1. 核对论文题名、作者、年份及当前结果标识。从该论文“引用/Cite”对话框选择实际支持的BibTeX或其他格式。
2. 读取导出内容核对元数据，保存到所属研究work；下载失败保留已核字段并报告，不能伪造文件或补出不存在的DOI。
3. 只有归档已授权时按 [Zotero规则](../paper-researcher/references/zotero-workflow.md) 查重再导入，读回父项及关联。仅导出书目不自动下载全文或生成笔记。
4. 全文、笔记、证据俱全时可用 `tools/zotero_archive.py`；它不解析BibTeX。当前插件缺导入能力时保留引文文件并标待归档，不能通过旧409会话状态推断成功。

验证码交用户，不自动重试挑战；额外付费逐篇确认。跨库引用量需注明来源与读取日期。
