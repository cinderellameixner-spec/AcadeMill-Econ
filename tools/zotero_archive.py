"""Archive an explicit literature batch using Zotero Web API via pyzotero.

Read-only planning by default; --apply enables the requested writes. Credentials
come only from process env or existing local Claude config and never enter logs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

from literature_state import atomic_write, inspect_pdf, load_json, normal_doi, note_html, record, validate_evidence


def credentials(expected_id):
    env = dict(os.environ)
    if not (env.get("ZOTERO_API_KEY") and env.get("ZOTERO_LIBRARY_ID")):
        config_path = Path.home() / ".claude.json"
        if config_path.exists():
            config = load_json(config_path)
            candidates = [s.get("env", {}) for name, s in config.get("mcpServers", {}).items()
                          if "zotero" in name.lower()]
            matches = [e for e in candidates if e.get("ZOTERO_API_KEY")
                       and str(e.get("ZOTERO_LIBRARY_ID")) == str(expected_id)]
            if len(matches) != 1:
                raise ValueError("No unique existing credential for the requested library")
            env = matches[0]
    if str(env.get("ZOTERO_LIBRARY_ID")) != str(expected_id):
        raise ValueError("Credential library differs from requested library")
    if env.get("ZOTERO_LIBRARY_TYPE", "user") != "user":
        raise ValueError("This helper supports the explicitly selected personal library only")
    if not env.get("ZOTERO_API_KEY"):
        raise ValueError("Missing existing Zotero write credential")
    return env["ZOTERO_API_KEY"]


def normalized_title(title):
    return re.sub(r"[\W_]+", "", title).casefold()


def created_key(response):
    values = response.get("successful") or response.get("success") or response.get("unchanged")
    if not values or response.get("failed"):
        raise ValueError("Zotero rejected creation; read back before retrying")
    value = next(iter(values.values()))
    return value if isinstance(value, str) else value["key"]


def find_parent(client, paper, tracked=None):
    metadata = paper["metadata"]
    doi = normal_doi(metadata.get("DOI"))

    def matches(item):
        data = item["data"]
        if data.get("itemType") != "journalArticle":
            return False
        existing_doi = normal_doi(data.get("DOI"))
        if doi and existing_doi:
            return doi == existing_doi
        return (normalized_title(data.get("title", "")) == normalized_title(metadata["title"])
                and bool(metadata.get("date")) and bool(data.get("date"))
                and str(data["date"])[:4] == str(metadata["date"])[:4])

    key = paper.get("item_key") or (tracked or {}).get("item_key")
    if key:
        item = client.item(key)
        if not matches(item):
            raise ValueError("Tracked Zotero item does not match the requested paper")
        return item
    candidates = {}
    for query in dict.fromkeys([doi, metadata["title"]]):
        if query:
            for item in client.everything(client.items(q=query, qmode="everything",
                                                       itemType="journalArticle", limit=100)):
                candidates[item["key"]] = item
    matched = [item for item in candidates.values() if matches(item)]
    if len(matched) > 1:
        raise ValueError("Multiple duplicate candidates; select a keeper explicitly")
    return matched[0] if matched else None


def verify_existing_pdf(paper, attachment):
    """Validate an explicitly supplied local Zotero copy with different bytes."""
    path = paper.get("existing_attachment_path")
    if not path or Path(path).parent.name != attachment["key"]:
        return False
    import fitz
    with fitz.open(path) as doc:
        if doc.is_encrypted or len(doc) != paper["_pdf"]["pdf_pages"]:
            return False
        text = doc[0].get_text()
        title_matches = normalized_title(paper["metadata"]["title"]) in normalized_title(text)
        doi = normal_doi(paper["metadata"].get("DOI"))
        doi_matches = bool(doi) and doi in text.lower().replace(" ", "")
        return bool(title_matches and doi_matches)


def resolve_collection(client, name, apply):
    matches = [c for c in client.everything(client.collections(limit=100))
               if c["data"]["name"] == name and not c["data"].get("parentCollection")]
    if len(matches) > 1:
        raise ValueError("Multiple root collections with the requested name")
    if matches:
        return matches[0]["key"]
    if apply:
        return created_key(client.create_collections([{"name": name, "parentCollection": False}]))
    return None


def archive(client, manifest, state_path, apply=False):
    library_id = manifest["library_id"]
    planned = []
    if not str(manifest.get("collection_name", "")).strip() or not manifest.get("papers"):
        raise ValueError("An explicit collection and nonempty batch are required")
    state = load_json(state_path) if Path(state_path).exists() else {"schema_version": 1, "papers": {}}
    if state.get("schema_version") != 1 or not isinstance(state.get("papers"), dict):
        raise ValueError("Unsupported state schema")
    ids, dois, parent_keys = set(), set(), set()
    # Validate every local input before any external mutation.
    for paper in manifest["papers"]:
        metadata = paper["metadata"]
        pdf = inspect_pdf(paper["pdf_path"])
        evidence = load_json(paper["evidence_path"])
        validate_evidence(evidence, actual_pages=pdf["pdf_pages"])
        if evidence["source_kind"] != "fulltext" or paper.get("reading_mode", "skim") not in {"skim", "deep"}:
            raise ValueError("PDF archive notes require fulltext evidence and skim/deep reading_mode")
        if not paper.get("paper_id") or not paper["metadata"].get("title"):
            raise ValueError("Each paper requires paper_id and verified metadata")
        if metadata.get("itemType") != "journalArticle":
            raise ValueError("This helper archives journalArticle records only")
        if not pdf["text_available"]:
            raise ValueError("Textless PDF needs separately verified OCR before fulltext archive")
        doi = normal_doi(metadata.get("DOI"))
        if not doi and not re.match(r"^\d{4}", str(metadata.get("date", ""))):
            raise ValueError("Records without DOI require a verified publication year")
        if (evidence["paper_id"] != paper["paper_id"]
                or normalized_title(evidence["title"]) != normalized_title(metadata["title"])
                or (evidence.get("doi") and normal_doi(evidence["doi"]) != doi)):
            raise ValueError("Evidence identity differs from paper metadata")
        if paper["paper_id"] in ids or (doi and doi in dois):
            raise ValueError("Duplicate paper ID or DOI within batch; use one record")
        ids.add(paper["paper_id"])
        if doi:
            dois.add(doi)
        tracked = state["papers"].get(paper["paper_id"], {})
        if tracked.get("library_id") and str(tracked["library_id"]) != str(library_id):
            raise ValueError("Tracked paper belongs to a different library")
        if tracked.get("doi") and normal_doi(tracked["doi"]) != doi:
            raise ValueError("Tracked DOI cannot change")
        if paper.get("item_key") and tracked.get("item_key") and paper["item_key"] != tracked["item_key"]:
            raise ValueError("Tracked item key cannot change")
        if doi and any(other != paper["paper_id"] and normal_doi(value.get("doi")) == doi
                       for other, value in state["papers"].items()):
            raise ValueError("DOI already tracked under another paper ID")
        paper["_pdf"] = pdf
        paper["_note"] = note_html(Path(paper["note_md"]).read_text(encoding="utf-8-sig"))
        if not paper["_note"].strip():
            raise ValueError("Reading note cannot be empty")
    # Check parents first, including explicitly selected local item keys.
    parents = {p["paper_id"]: find_parent(client, p, state["papers"].get(p["paper_id"]))
               for p in manifest["papers"]}
    for parent in parents.values():
        if parent:
            if parent["key"] in parent_keys:
                raise ValueError("Batch maps multiple records to the same parent")
            parent_keys.add(parent["key"])
    collection_key = resolve_collection(client, manifest["collection_name"], apply)
    if not apply:
        return {"apply": False, "collection_key": collection_key,
                "papers": [{"paper_id": p["paper_id"], "existing_item_key":
                            parents[p["paper_id"]]["key"] if parents[p["paper_id"]] else None}
                           for p in manifest["papers"]]}
    for paper in manifest["papers"]:
        metadata = paper["metadata"]
        reading_mode = paper.get("reading_mode", "skim")
        reading_tag = "AI精读完成" if reading_mode == "deep" else "AI泛读完成"
        data = {"paper_id": paper["paper_id"], "title": metadata["title"], "doi": metadata.get("DOI"),
                "library_id": library_id, "collection_key": collection_key,
                "source_kind": "fulltext", "evidence_path": paper["evidence_path"],
                "reading_status": "deep_verified" if reading_mode == "deep" else "skim_verified", "pdf_status": "verified",
                **{k: v for k, v in paper["_pdf"].items() if k in {"pdf_path", "pdf_sha256", "pdf_pages"}}}

        def save():
            record(state_path, data)

        try:
            parent = parents[paper["paper_id"]]
            if parent is None:
                parent = client.item(created_key(client.create_items([
                    dict(metadata, collections=[collection_key], tags=[{"tag": t} for t in manifest.get("tags", [])])
                ])))
            key = parent["key"]
            data.update(item_key=key, metadata_status="verified")
            save()
            if collection_key not in parent["data"].get("collections", []):
                parent["data"]["collections"] = parent["data"].get("collections", []) + [collection_key]
                client.update_item(parent)
            if collection_key not in client.item(key)["data"].get("collections", []):
                raise ValueError("Collection membership was not verified")
            data["collection_status"] = "verified"
            save()
            children = client.everything(client.children(key, limit=100))
            md5 = hashlib.md5(Path(paper["pdf_path"]).read_bytes()).hexdigest()
            matching = [c for c in children if c["data"].get("itemType") == "attachment"
                        and c["data"].get("contentType") == "application/pdf"
                        and c["data"].get("md5") == md5]
            if not matching:
                matching = [c for c in children if c["data"].get("itemType") == "attachment"
                            and c["data"].get("parentItem") == key
                            and verify_existing_pdf(paper, c)]
                if matching:
                    data["attachment_verification"] = "explicit_local_Zotero_PDF_title_DOI_pages"
            if not matching:
                pending = [c for c in children if c["data"].get("itemType") == "attachment"
                           and c["data"].get("filename") == Path(paper["pdf_path"]).name]
                if pending and pending[0]["data"].get("md5"):
                    data["attachment_status"] = "blocked"
                    data["error"] = "Existing filename attachment needs file verification; no duplicate uploaded"
                else:
                    pdf_path = Path(paper["pdf_path"]).resolve()
                    if pending:
                        template = dict(pending[0]["data"])
                    else:
                        template = client.item_template("attachment", linkmode="imported_file")
                    # Only basename enters the API; Windows absolute paths are not valid filenames.
                    template.update(filename=pdf_path.name, title=pdf_path.stem,
                                    contentType="application/pdf", parentItem=key)
                    result = client.upload_attachments([template], parentid=key, basedir=str(pdf_path.parent))
                    if result.get("failure"):
                        data["error"] = "Attachment creation rejected; local PDF retained"
                    matching = [c for c in client.everything(client.children(key, limit=100))
                                if c["data"].get("md5") == md5
                                and c["data"].get("parentItem") == key]
            if matching:
                data.update(attachment_key=matching[0]["key"], attachment_status="verified")
            elif data.get("attachment_status") != "blocked":
                data["attachment_status"] = "failed"
                data["error"] = "PDF upload not verified; local file retained"
            save()
            content = paper["_note"]
            note = content
            children = client.everything(client.children(key, limit=100))
            same = [c for c in children if c["data"].get("itemType") == "note"
                    and note.strip() == c["data"].get("note", "").strip()]
            if same:
                note_key = same[0]["key"]
            else:
                note_key = created_key(client.create_items([{"itemType": "note", "parentItem": key,
                                                            "note": note, "tags": [{"tag": reading_tag}]}]))
            verified = client.item(note_key)["data"]
            if verified.get("parentItem") != key or note.strip() != verified.get("note", "").strip():
                raise ValueError("Note content or parent link was not verified")
            data.update(note_keys=[note_key], note_status="verified")
            parent = client.item(key)
            tags = parent["data"].get("tags", [])
            if not any(t.get("tag") == reading_tag for t in tags):
                parent["data"]["tags"] = tags + [{"tag": reading_tag}]
                client.update_item(parent)
            if not any(t.get("tag") == reading_tag for t in client.item(key)["data"].get("tags", [])):
                raise ValueError("AI reading tag was not verified")
            if data.get("attachment_status") == "verified":
                data["error"] = None
            save()
        except Exception as exc:
            # Error class is useful; raw exception text may include sensitive HTTP details.
            data["error"] = type(exc).__name__ + ": archive step failed; retry only unverified stages"
            data.setdefault("note_status", "blocked")
            save()
        planned.append(data)
    return {"apply": True, "collection_key": collection_key, "papers": planned}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--state", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        from pyzotero import zotero
        manifest = load_json(args.manifest)
        client = zotero.Zotero(manifest["library_id"], "user", credentials(manifest["library_id"]))
        result = archive(client, manifest, args.state, args.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.apply and any(p.get("note_status") != "verified" or p.get("attachment_status") != "verified" or p.get("error")
                              for p in result["papers"]):
            parser.exit(1, "Partial archive; see state file for verified and pending stages.\n")
    except Exception as exc:
        parser.exit(1, "Archive unavailable: " + type(exc).__name__ + "; no credential details logged.\n")


if __name__ == "__main__":
    main()
