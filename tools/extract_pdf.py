import sys, fitz, io
doc = fitz.open(sys.argv[1])
start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
end = int(sys.argv[3]) if len(sys.argv) > 3 else doc.page_count
out = sys.argv[4] if len(sys.argv) > 4 else None
buf = io.StringIO()
buf.write(f"PAGES: {doc.page_count}\n")
for i in range(start-1, min(end, doc.page_count)):
    buf.write(f"\n===== PAGE {i+1} =====\n")
    buf.write(doc[i].get_text())
if out:
    with open(out, "w", encoding="utf-8") as f:
        f.write(buf.getvalue())
else:
    sys.stdout.reconfigure(encoding="utf-8")
    print(buf.getvalue())
