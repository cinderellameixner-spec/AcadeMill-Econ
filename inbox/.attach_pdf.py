"""Attach a local PDF to a Zotero item created via push_to_zotero.py within the same session.

Usage: py attach_pdf.py <session_id> <item_index> <pdf_path> [title]

Zotero Connector's saveAttachment uses the session-internal item ID
(format: cnki_<session>_<index>) created earlier by saveItems.
"""

import json
import sys
import urllib.request
import urllib.error

ZOTERO_API = 'http://127.0.0.1:23119/connector'


def main():
    if len(sys.argv) < 4:
        print('Usage: py attach_pdf.py <session_id> <item_index> <pdf_path> [title]')
        sys.exit(1)
    session_id = sys.argv[1]
    item_index = int(sys.argv[2])
    pdf_path = sys.argv[3]
    title = sys.argv[4] if len(sys.argv) > 4 else 'Full Text PDF'

    item_id = f'cnki_{session_id}_{item_index}'

    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    print(f'PDF size: {len(pdf_bytes)} bytes')

    metadata = json.dumps({
        'id': item_id + '_pdf',
        'parentItemID': item_id,
        'title': title,
        'url': f'file:///{pdf_path}',
        'contentType': 'application/pdf',
    })
    url = f'{ZOTERO_API}/saveAttachment?sessionID={session_id}'
    req = urllib.request.Request(url, data=pdf_bytes, headers={
        'Content-Type': 'application/pdf',
        'X-Metadata': metadata,
        'Content-Length': str(len(pdf_bytes)),
        'X-Zotero-Connector-API-Version': '3',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        print(f'OK: status={resp.status}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'HTTPError {e.code}: {body}')
        sys.exit(2)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(3)


if __name__ == '__main__':
    main()
