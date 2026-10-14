# Zotero归档、阅读与恢复

本规则替代旧工作流中“仅请求归档才写入”以及按409判断成功等说明。默认行为由 [文献协同指南](../../../../docs/LITERATURE_WORKFLOW.md) 定义；一次请求的明确限制优先。

## 归属与查重

正式研究先按research/AGENTS.md确定项目与本轮记录；维护验收放根work/。记录当前库ID和指定合集key，不能假定读库意味着写权限；不切换用户未指定的群组库。

导入前按DOI及标题搜索候选，必要时用metadata核对题名、作者、年份、类型和DOI。标题归一化仅用于匹配，不改展示书目；不同DOI、预印本/发表版或不同年份不能自动合并。短关键词空命中时交叉检查DOI/作者，不依语义相似度直接认定重复或不存在。

search_collections按名称返回后核对完整名称与层级；不将局部匹配当目标合集。有确切项目授权时缺合集可创建；存在多个同名合集时读取层级消歧。添加已有文献用manage_collections增量加入，标签用add_tags，不替换用户已有合集或标签。

## 导入与验证

- 新文献已有本地PDF：核对可打开、页数、题名/作者/DOI；使用实际add_from_file的绝对路径，读取生成的书目与附件，核对并仅修正已验证字段。中文作者/期刊优先核原刊与首页，不盲信CrossRef或文件名猜测。
- 只有书目：使用实际DOI/CSL/BibTeX工具；不假定自动获取PDF或继承校园登录。校园全文通过同一Edge下载。
- 已有父条目：复用；有匹配PDF则不重复上传，没有则仅补附件。没有可用补附件方法时记录pending_attachment，保留PDF和原条目，不用add_from_file制造重复父项。
- 创建调用超时或返回格式不明确时先查重读回，避免重试造成重复。书目创建成功而附件失败时记partial，下一轮只恢复缺失阶段。
- 当前GPT工具处于local-only时，可用tools/zotero_archive.py作为同一个人库的写入补充：仅从进程环境或既有本机Claude配置在内存读取凭据，manifest.library_id必须匹配，不修改插件全局配置。默认命令只做计划，按用户已授权动作加--apply才写入。辅助工具不生成阅读内容，需要已核书目、PDF、泛读笔记与证据文件。
- manifest为library_id、collection_name、可选tags和papers列表；每篇包含paper_id、metadata（Zotero格式）、pdf_path、note_md、evidence_path，可选item_key。例：`python tools/zotero_archive.py '研究目录/work/manifest.json' --state '研究目录/work/literature_state.json' --apply`。先不加--apply核对只读计划，再执行；已有PDF不同下载批次可能字节不同，可通过get_attachment_path取得实际Zotero副本，填existing_attachment_path核对题名/DOI/页数后复用。
- 所有路径相对于当前工作目录，建议从仓库根目录执行。清单格式示例（占位符须替换为实际已核材料，library_id不含密钥）：

```json
{
  "library_id": "<your-personal-library-id>",
  "collection_name": "<explicitly-selected-root-collection>",
  "papers": [{
    "paper_id": "P001",
    "reading_mode": "skim",
    "metadata": {
      "itemType": "journalArticle",
      "title": "<verified-title>",
      "date": "<verified-year>",
      "creators": [{"creatorType": "author", "name": "<verified-author>"}]
    },
    "pdf_path": "research/<project>/inbox/paper.pdf",
    "note_md": "research/<project>/output/note.md",
    "evidence_path": "research/<project>/work/evidence.json"
  }]
}
```

- DOI仅在已核实存在时填写；已有条目可补item_key。同库同ID重复执行复用已核键；读回与附件哈希不符时停止该阶段，不能为重试制造新父项。缺凭据保留本地成果；只读计划也需要该库读取权限，不是无网络演练。
- 云端写入后Web API读回与桌面同步分别记录；当前MCP读本地模式可能暂时看不到云端新子项，不能因此重复导入。自动同步后再核对桌面，不把云端读回误称为桌面同步验收。实际Web API和文件上传流程参考官方文档：https://www.zotero.org/support/dev/web_api/v3/write_requests 与 https://www.zotero.org/support/dev/web_api/v3/file_upload。
- 辅助manifest每篇可设reading_mode为skim/deep（默认skim），分别保存AI泛读/精读状态。工具只归档已由agent完成的阅读成果，不自动认定精读；摘要级记录使用MCP直接建子笔记并保留abstract_only状态，不放入此PDF全文归档批次。
- 读取metadata确认书目/合集；读取children确认PDF的parentItem、格式与文件名；读取附件路径或文件内容核对可访问性。笔记读取验证标题、内容与parentItem。完成是这些证据齐备，不是接口返回201。

## 阅读与笔记

泛读/精读先检查已有同文献、同模式、同来源版本的笔记。已有完整精读时可据其生成摘要，复用笔记；明确重新阅读才出新版本。笔记标题为“泛读笔记/精读笔记—日期—vN”，项目笔记另加研究ID。写前get_notes检查，内容相同复用，内容变化追加版本，不覆盖人工笔记。

读取全文时核对实际页数和文本覆盖；get_item_fulltext可能有限页配置，必要时按页读取或获取本地附件路径。没有PDF时只按摘要说明；空文本扫描件记录OCR待完成。数字、表号、页码必须可定位。

先落盘笔记Markdown与证据记录，转为简单HTML再create_note挂父条目。可用tools/literature_state.py note-html转义正文，保留段落与公式原文；不要把Markdown源码冒充富文本。生成后读取notes核对子项、AI生成标识与内容，成功再增量添加AI阅读标签。

对比与综合成果在项目output保留唯一版本；需要Zotero回写时给参与文献分别添加带研究ID的关联子笔记，注明综合成果版本/来源。当前create_note仅支持父项子笔记，不虚构standalone参数或一个笔记挂多个父项。

## 本地状态与恢复

每批在项目work/literature_state.json记录：paper_id/title/doi/source/pdf_path/pdf_sha256/pdf_pages/library_id/item_key/collection_key/attachment_key/note_keys/evidence_path，以及metadata_status/pdf_status/attachment_status/reading_status/note_status/collection_status/error。

状态取pending、verified、failed、blocked、not_requested；reading_status另取abstract_only、skim_verified、deep_verified。使用tools/literature_state.py record增量更新。重复执行复用键和SHA256；记录错误不保存密钥、Cookie或完整网络头。错误解决后只补未完成阶段。

最终反馈每篇书目、附件、阅读、笔记和合集状态以及本地成果。库离线、权限/存储失败时继续已授权本地阅读，明确归档待完成；不把“本地PDF已保存”说成“Zotero附件已保存”。
