"""Offline archive tests: no Zotero/network access or live library writes."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from zotero_archive import archive, find_parent


class FakeClient:
    def __init__(self):
        self.entries = {}
        self.colls = []
        self.fail_upload = False
        self.uploads = 0
        self.counter = 0

    def everything(self, values):
        return values

    def item(self, key):
        return copy.deepcopy(self.entries[key])

    def items(self, **kwargs):
        return [copy.deepcopy(v) for v in self.entries.values()
                if v['data'].get('itemType') == 'journalArticle']

    def children(self, key, **kwargs):
        return [copy.deepcopy(v) for v in self.entries.values() if v['data'].get('parentItem') == key]

    def collections(self, **kwargs):
        return copy.deepcopy(self.colls)

    def create_collections(self, values):
        self.colls.append({'key': 'COLL0001', 'data': values[0]})
        return {'successful': {'0': {'key': 'COLL0001'}}}

    def create_items(self, values):
        self.counter += 1
        key = f'ITEM{self.counter:04}'
        self.entries[key] = {'key': key, 'data': copy.deepcopy(values[0])}
        return {'successful': {'0': {'key': key}}}

    def update_item(self, item):
        self.entries[item['key']] = copy.deepcopy(item)

    def item_template(self, *args, **kwargs):
        return {'itemType': 'attachment', 'linkMode': 'imported_file'}

    def upload_attachments(self, values, parentid=None, basedir=None):
        self.uploads += 1
        value = values[0]
        assert not Path(value['filename']).is_absolute(), 'API filename must be basename'
        assert Path(basedir, value['filename']).is_file()
        if self.fail_upload:
            return {'failure': values}
        value = dict(value, parentItem=parentid,
                     md5=hashlib.md5(Path(basedir, value['filename']).read_bytes()).hexdigest())
        self.create_items([value])
        return {'success': [value]}


class ArchiveChecks(unittest.TestCase):
    def fixture(self, directory):
        base = Path(directory)
        pdf = base / 'paper.pdf'
        doc = fitz.open()
        doc.new_page().insert_text((50, 50), 'Test Paper DOI:10.1/test')
        doc.save(pdf)
        doc.close()
        note = base / 'note.md'
        note.write_text('# Reading note\n\nVerified source.', encoding='utf-8')
        evidence = base / 'evidence.json'
        evidence.write_text(json.dumps({'paper_id': 'p1', 'title': 'Test Paper', 'source_kind': 'fulltext',
                                        'pdf_pages': 1, 'claims': [{'claim_id': 'C1', 'statement': 'Test',
                                                                  'origin': 'paper', 'pdf_page': 1,
                                                                  'locator': 'Abstract'}]}), encoding='utf-8')
        return {'library_id': 1, 'collection_name': 'Test', 'papers': [
            {'paper_id': 'p1', 'metadata': {'itemType': 'journalArticle', 'title': 'Test Paper',
                                           'DOI': '10.1/test', 'date': '2025'},
             'pdf_path': str(pdf), 'note_md': str(note), 'evidence_path': str(evidence)}]}

    def test_plan_is_read_only_and_repeat_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            state = Path(tmp) / 'state.json'
            archive(client, copy.deepcopy(manifest), state)
            self.assertFalse(client.entries)
            self.assertFalse(client.colls)
            self.assertFalse(state.exists())
            first = archive(client, copy.deepcopy(manifest), state, apply=True)
            keys = set(client.entries)
            second = archive(client, copy.deepcopy(manifest), state, apply=True)
            self.assertEqual(keys, set(client.entries))
            self.assertEqual(client.uploads, 1)
            self.assertEqual(first['papers'][0]['item_key'], second['papers'][0]['item_key'])
            self.assertEqual(second['papers'][0]['note_status'], 'verified')

    def test_upload_failure_preserves_parent_and_note_for_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            state = Path(tmp) / 'state.json'
            client.fail_upload = True
            first = archive(client, copy.deepcopy(manifest), state, apply=True)['papers'][0]
            self.assertEqual(first['attachment_status'], 'failed')
            self.assertEqual(first['note_status'], 'verified')
            client.fail_upload = False
            resumed = archive(client, copy.deepcopy(manifest), state, apply=True)['papers'][0]
            self.assertEqual(first['item_key'], resumed['item_key'])
            self.assertEqual(first['note_keys'], resumed['note_keys'])
            self.assertEqual(resumed['attachment_status'], 'verified')
            self.assertIsNone(resumed['error'])

    def test_deep_reading_is_not_labeled_skim(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            manifest['papers'][0]['reading_mode'] = 'deep'
            result = archive(client, manifest, Path(tmp) / 'state.json', apply=True)['papers'][0]
            self.assertEqual(result['reading_status'], 'deep_verified')
            self.assertNotIn({'tag': 'AI泛读完成'}, client.item(result['item_key'])['data']['tags'])

    def test_no_doi_explicit_item_key_must_match_identity(self):
        client = FakeClient()
        client.entries['EXISTING'] = {'key': 'EXISTING', 'data': {
            'itemType': 'journalArticle', 'title': 'Another Paper', 'date': '2025'}}
        paper = {'item_key': 'EXISTING', 'metadata': {
            'title': 'Requested Paper', 'date': '2025', 'itemType': 'journalArticle'}}
        with self.assertRaises(ValueError):
            find_parent(client, paper)
        client.entries['EXISTING']['data']['title'] = 'Requested Paper'
        self.assertEqual(find_parent(client, paper)['key'], 'EXISTING')

    def test_conflicting_dois_are_not_merged_by_title(self):
        client = FakeClient()
        client.entries['EXISTING'] = {'key': 'EXISTING', 'data': {
            'itemType': 'journalArticle', 'title': 'Test Paper', 'date': '2025', 'DOI': '10.1/other'}}
        paper = {'metadata': {'title': 'Test Paper', 'date': '2025', 'DOI': '10.1/test'}}
        self.assertIsNone(find_parent(client, paper))

    def test_duplicate_batch_blocks_before_collection_or_item_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            manifest['papers'].append(copy.deepcopy(manifest['papers'][0]))
            with self.assertRaises(ValueError):
                archive(client, manifest, Path(tmp) / 'state.json', apply=True)
            self.assertFalse(client.colls)
            self.assertFalse(client.entries)

    def test_evidence_identity_blocks_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            path = Path(manifest['papers'][0]['evidence_path'])
            data = json.loads(path.read_text(encoding='utf-8'))
            data['title'] = 'Unrelated Paper'
            path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                archive(client, manifest, Path(tmp) / 'state.json', apply=True)
            self.assertFalse(client.colls)
            self.assertFalse(client.entries)

    def test_state_library_conflict_blocks_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest, client = self.fixture(tmp), FakeClient()
            state = Path(tmp) / 'state.json'
            state.write_text(json.dumps({'schema_version': 1, 'papers': {
                'p1': {'library_id': 2}}}), encoding='utf-8')
            with self.assertRaises(ValueError):
                archive(client, manifest, state, apply=True)
            self.assertFalse(client.colls)
            self.assertFalse(client.entries)


if __name__ == '__main__':
    unittest.main()
