"""Local helpers for literature evidence, HTML notes and resumable archive state.

No network access or Zotero mutations. Requires Python 3.10+.
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False, suffix=".tmp") as handle:
            temp_path = Path(handle.name)
            handle.write(text)
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def inspect_pdf(path):
    import fitz
    path = Path(path).resolve(strict=True)
    with fitz.open(path) as doc:
        if doc.is_encrypted or not doc.page_count:
            raise ValueError("PDF is encrypted or empty")
        text = "\n".join(page.get_text() for page in doc)
        return {"pdf_path": str(path), "pdf_pages": doc.page_count,
                "pdf_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size, "text_characters": len(text),
                "text_available": bool(text.strip())}


def validate_evidence(data, actual_pages=None):
    if not data.get("paper_id") or not data.get("title"):
        raise ValueError("Evidence requires paper_id and title")
    kind = data.get("source_kind")
    if kind not in {"fulltext", "abstract"}:
        raise ValueError("source_kind must be fulltext or abstract")
    pages = data.get("pdf_pages")
    if kind == "fulltext":
        if type(pages) is not int or pages < 1:
            raise ValueError("Fulltext evidence requires a positive PDF page count")
        if actual_pages is not None and actual_pages != pages:
            raise ValueError("Declared PDF page count differs from the actual file")
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("Evidence requires nonempty claims")
    ids = set()
    for claim in claims:
        key = claim.get("claim_id")
        if not key or key in ids or not claim.get("statement"):
            raise ValueError("Claims require unique IDs and statements")
        ids.add(key)
        if claim.get("origin") not in {"paper", "researcher", "model"}:
            raise ValueError("Invalid claim origin")
        page = claim.get("pdf_page")
        if page is not None and (type(page) is not int or kind != "fulltext"
                                 or not 1 <= page <= pages):
            raise ValueError("PDF page is invalid or invented for abstract-only evidence")
        if claim["origin"] == "paper":
            if not claim.get("locator"):
                raise ValueError("Paper claims require a locator")
            if kind == "fulltext" and page is None:
                raise ValueError("Fulltext paper claims require a PDF page")
            if kind == "abstract" and not (claim.get("source_url") or data.get("source_url")):
                raise ValueError("Abstract claims require a source URL")
    return {"valid": True, "claims": len(claims)}


def normal_doi(value):
    value = (value or "").strip().lower()
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)


def validate_record(data):
    states = {"pending", "verified", "failed", "blocked", "not_requested"}
    for field in ("metadata_status", "pdf_status", "attachment_status",
                  "note_status", "collection_status"):
        if field in data and data[field] not in states:
            raise ValueError(f"Invalid {field}")
    if data.get("reading_status") not in {None, "pending", "failed", "blocked",
                                           "not_requested", "abstract_only",
                                           "skim_verified", "deep_verified"}:
        raise ValueError("Invalid reading_status")
    for stage, fields in {
        "metadata_status": ["library_id", "item_key"],
        "pdf_status": ["pdf_path", "pdf_sha256", "pdf_pages"],
        "attachment_status": ["item_key", "attachment_key"],
        "note_status": ["item_key", "note_keys"],
        "collection_status": ["item_key", "collection_key"],
    }.items():
        if data.get(stage) == "verified" and any(not data.get(f) for f in fields):
            raise ValueError(f"{stage}=verified requires {', '.join(fields)}")
    if data.get("reading_status") in {"skim_verified", "deep_verified"}:
        if data.get("source_kind") != "fulltext" or not data.get("evidence_path"):
            raise ValueError("Verified reading requires fulltext and an evidence path")


def record(state_path, patch):
    key = patch.get("paper_id")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Record patch requires paper_id")
    state_path = Path(state_path)
    state = load_json(state_path) if state_path.exists() else {"schema_version": 1, "papers": {}}
    if state.get("schema_version") != 1 or not isinstance(state.get("papers"), dict):
        raise ValueError("Unsupported state schema")
    old = state["papers"].get(key, {})
    incoming_doi = normal_doi(patch.get("doi"))
    if incoming_doi and normal_doi(old.get("doi")) not in {"", incoming_doi}:
        raise ValueError("Cannot change the DOI of a tracked paper")
    merged = dict(old, **patch)
    doi = normal_doi(merged.get("doi"))
    if doi and any(other != key and normal_doi(p.get("doi")) == doi
                   for other, p in state["papers"].items()):
        raise ValueError("DOI already tracked under another paper_id; reuse that record")
    for field in ("library_id", "item_key"):
        if old.get(field) and patch.get(field) and old[field] != patch[field]:
            raise ValueError(f"Cannot silently replace tracked {field}")
    validate_record(merged)
    state["papers"][key] = merged
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    return merged


def note_html(text):
    """Render paragraphs, headings, lists and bold; escape all input HTML."""
    blocks, paragraph = [], []
    list_open = False

    def inline(line):
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(line))

    def flush():
        if paragraph:
            blocks.append("<p>" + "<br/>".join(paragraph) + "</p>")
            paragraph.clear()

    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if not bullet and list_open:
            blocks.append("</ul>")
            list_open = False
        if heading:
            flush()
            blocks.append("<p><strong>" + inline(heading[1]) + "</strong></p>")
        elif bullet:
            flush()
            if not list_open:
                blocks.append("<ul>")
                list_open = True
            blocks.append("<li>" + inline(bullet[1]) + "</li>")
        elif not line.strip():
            flush()
        else:
            paragraph.append(inline(line))
    flush()
    if list_open:
        blocks.append("</ul>")
    return "\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect-pdf")
    inspect.add_argument("pdf")
    evidence = sub.add_parser("validate-evidence")
    evidence.add_argument("evidence")
    evidence.add_argument("--pdf")
    update = sub.add_parser("record")
    update.add_argument("state")
    update.add_argument("patch")
    note = sub.add_parser("note-html")
    note.add_argument("markdown")
    note.add_argument("output")
    args = parser.parse_args()
    try:
        if args.command == "inspect-pdf":
            result = inspect_pdf(args.pdf)
        elif args.command == "validate-evidence":
            pages = inspect_pdf(args.pdf)["pdf_pages"] if args.pdf else None
            result = validate_evidence(load_json(args.evidence), pages)
        elif args.command == "record":
            result = record(args.state, load_json(args.patch))
        else:
            atomic_write(args.output, note_html(Path(args.markdown).read_text(encoding="utf-8-sig")))
            result = {"html_path": str(Path(args.output).resolve())}
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
