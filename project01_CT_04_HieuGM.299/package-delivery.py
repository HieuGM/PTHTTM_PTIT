"""Package reproducible source, model artifacts and report; verify every hash."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
STEM = ROOT.name
archive = ROOT.parent / (STEM + '.zip')
manifest_path = ROOT / 'submission-manifest.json'
excluded_dirs = {'__pycache__', '.pytest_cache', 'runtime', 'preview', '.git',
                 '.ipynb_checkpoints', 'diacare-notebook-output'}


def include(path):
    relative = path.relative_to(ROOT)
    if any(part in excluded_dirs for part in relative.parts):
        return False
    if relative.parts[:2] in {('data', 'raw'), ('data', 'splits')}:
        return False
    return path != manifest_path and path.suffix not in {'.zip', '.pyc'} and path.name != '.env'


files = sorted(path for path in ROOT.rglob('*') if path.is_file() and include(path))
entries = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest = {'project': STEM, 'student': 'Giáp Minh Hiếu', 'student_id': 'B23DCCN299',
            'files': entries, 'excluded': ['raw data', 'split caches', 'runtime database', 'QA page images', 'credentials'],
            'manifest_excludes_itself': True}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for path in files + [manifest_path]:
        output.write(path, f'{STEM}/{path.relative_to(ROOT).as_posix()}')
with zipfile.ZipFile(archive) as output:
    assert output.testzip() is None
    for entry in entries:
        raw = output.read(f"{STEM}/{entry['path']}")
        assert len(raw) == entry['bytes']
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
print(json.dumps({'archive': str(archive), 'files': len(entries)+1,
                  'bytes': archive.stat().st_size, 'crc_and_sha256': 'passed'}, ensure_ascii=False))
