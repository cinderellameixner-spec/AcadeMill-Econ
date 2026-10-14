"""Check reusable source packaging; never read credentials or research folders."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def check(root=ROOT):
    baseline = json.loads((root / 'docs/legacy_sha256.json').read_text(encoding='utf-8'))
    for relative, sha in baseline['files'].items():
        if digest(root / relative) != sha:
            raise ValueError(f'Preserved legacy source changed: {relative}')

    sources = [root / p for p in ('AGENTS.md', 'README.md', 'CODEX_SETUP.md',
                                  'paper-reading/AGENTS.md', 'research/AGENTS.md',
                                  '.codex/config.example.toml')]
    sources += list(root.glob('requirements*.txt'))
    for folder in ('.agents/skills', 'docs', 'tools', 'tests', '.github'):
        sources += [p for p in (root / folder).rglob('*')
                    if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.md', '.py', '.ps1', '.yml', '.json'}]
    sources = sorted(set(p for p in sources if p.relative_to(root).as_posix() not in baseline['files']))
    for path in sources:
        text = path.read_text(encoding='utf-8-sig')
        if re.search(r'(?i)[cd]:[/\\](?:users|app|mydesktop)[/\\]', text):
            raise ValueError(f'Private machine path in new source: {path.relative_to(root)}')
        if path.suffix == '.py':
            ast.parse(text, filename=str(path))
        elif path.suffix == '.md':
            body = re.sub(r'```.*?```', '', text, flags=re.S)
            for target in re.findall(r'\]\(([^)]+)\)', body):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                local = target.split('#')[0].strip('<>')
                if not (path.parent / local).exists():
                    raise ValueError(f'Broken link: {path.relative_to(root)} -> {target}')

    skills = sorted((root / '.agents/skills').glob('*/SKILL.md'))
    if not skills:
        raise ValueError('No packaged skills')
    names = set()
    for skill in skills:
        text = skill.read_text(encoding='utf-8-sig')
        front = re.match(r'^---\s*\n(.*?)\n---', text, re.S)
        if not front:
            raise ValueError(f'Missing skill frontmatter: {skill.parent.name}')
        data = yaml.safe_load(front[1])
        name, description = data.get('name'), data.get('description')
        if (not isinstance(name, str) or not re.fullmatch(r'[a-z0-9-]{1,64}', name)
                or name != skill.parent.name or name in names
                or not isinstance(description, str) or not description.strip()):
            raise ValueError(f'Invalid skill metadata: {skill.parent.name}')
        names.add(name)
    required = {'paper-reader', 'topic-selection', 'research-design', 'data-empirical',
                'paper-writing', 'academic-presentation', 'paper-researcher',
                'literature-supplement', 'cnki-researcher', 'wos-researcher', 'gs-researcher'}
    if not required <= names:
        raise ValueError('Required workflow skill missing')
    workflow = yaml.safe_load((root / '.github/workflows/check.yml').read_text(encoding='utf-8'))
    if not workflow.get('jobs'):
        raise ValueError('Missing CI jobs')
    if sys.version_info >= (3, 11):
        import tomllib
        config = tomllib.loads((root / '.codex/config.example.toml').read_text(encoding='utf-8'))
        if set(config['mcp_servers']) != {'cnki-browser', 'gs-browser', 'zotero'}:
            raise ValueError('Invalid MCP example')
    return {'new_source_files': len(sources), 'skills': len(skills),
            'preserved_legacy_files': len(baseline['files'])}


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False))
