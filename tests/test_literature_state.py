"""Offline invariants for resumable literature records and evidence validation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("literature_state", root / "tools/literature_state.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LiteratureChecks(unittest.TestCase):
    def test_resume_preserves_prior_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            module.record(state, {"paper_id": "p1", "doi": "https://doi.org/10.1/test",
                                  "library_id": 1, "item_key": "ABCDEFGH", "metadata_status": "verified",
                                  "attachment_status": "failed"})
            data = module.record(state, {"paper_id": "p1", "attachment_key": "ATTACH01",
                                         "attachment_status": "verified"})
            self.assertEqual(data["item_key"], "ABCDEFGH")
            self.assertEqual(data["metadata_status"], "verified")
            self.assertEqual(len(module.load_json(state)["papers"]), 1)
            with self.assertRaises(ValueError):
                module.record(state, {"paper_id": "p2", "doi": "DOI:10.1/TEST"})
            with self.assertRaises(ValueError):
                module.record(state, {"paper_id": "p1", "item_key": "DIFFERNT"})
            self.assertEqual(len(module.load_json(state)["papers"]), 1)

    def test_partial_archive_is_not_verified(self):
        with self.assertRaises(ValueError):
            module.validate_record({"attachment_status": "verified", "item_key": "ABCDEFGH"})
        with self.assertRaises(ValueError):
            module.validate_record({"note_status": "verified", "item_key": "ABCDEFGH"})
        with self.assertRaises(ValueError):
            module.validate_record({"reading_status": "deep_verified", "source_kind": "abstract"})

    def test_citations_must_fit_actual_source(self):
        data = {"paper_id": "p1", "title": "Paper", "source_kind": "fulltext", "pdf_pages": 3,
                "claims": [{"claim_id": "C1", "statement": "Claim", "origin": "paper",
                            "pdf_page": 2, "locator": "Methods"}]}
        self.assertTrue(module.validate_evidence(data, actual_pages=3)["valid"])
        with self.assertRaises(ValueError):
            module.validate_evidence(data, actual_pages=2)
        data["claims"][0]["pdf_page"] = 4
        with self.assertRaises(ValueError):
            module.validate_evidence(data)
        data["source_kind"] = "abstract"
        data["source_url"] = "https://example.org/abstract"
        with self.assertRaises(ValueError):
            module.validate_evidence(data)
        data["claims"][0].pop("pdf_page")
        self.assertTrue(module.validate_evidence(data)["valid"])

    def test_note_html_preserves_text_without_raw_markup(self):
        result = module.note_html('# Title\n\n- **Finding**: <script>x</script>\n\n$y = x$ & evidence')
        self.assertIn('<strong>Title</strong>', result)
        self.assertIn('<ul>', result)
        self.assertIn('<strong>Finding</strong>', result)
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)
        self.assertIn('$y = x$', result)
        self.assertIn('&amp;', result)


if __name__ == '__main__':
    unittest.main()
