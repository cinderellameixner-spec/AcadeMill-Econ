"""Research folder creation and isolation, without real study material."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('research_project', root / 'tools/research_project.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResearchChecks(unittest.TestCase):
    def test_ids_runs_and_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / 'research'
            first, run = module.create_project(base, '数字化/就业')
            second, _ = module.create_project(base, '数字化/就业')
            self.assertEqual(first.name, 'R001_数字化_就业')
            self.assertEqual(second.name, 'R002_数字化_就业')
            original = {p.relative_to(second): p.read_bytes() for p in second.rglob('*') if p.is_file()}
            resumed = module.create_run(module.resolve(base, 'R001'), '继续评估')
            self.assertNotEqual(resumed, run)
            self.assertTrue(run.is_dir())
            self.assertIn('+08:00', (first / 'PROJECT.md').read_text(encoding='utf-8'))
            self.assertEqual(original, {p.relative_to(second): p.read_bytes() for p in second.rglob('*') if p.is_file()})
            self.assertEqual(len(module.projects(base)), 2)
            self.assertFalse(list(base.glob('.*.reserved')))

    def test_invalid_project_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            module.create_project(base, 'Example')
            for invalid in ('../R001', 'R999', ''):
                with self.assertRaises(ValueError):
                    module.resolve(base, invalid)


if __name__ == '__main__':
    unittest.main()
