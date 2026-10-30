"""Package verified deliverables and reproducible sources, then verify ZIP."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
STEM = 'agent02_CT_04_hieugm'
pdf = ROOT/'report'/f'{STEM}.pdf'
assert pdf.is_file()
audit = json.loads((ROOT/'report/preview/audit.json').read_text(encoding='utf-8'))
assert audit['all_passed'] and audit.get('visual_review') == 'all 14 final pages inspected'
files = sorted(f for f in ROOT.rglob('*') if f.is_file()
               and '__pycache__' not in f.parts and f.suffix != '.pyc'
               and ('preview' not in f.parts or f == ROOT/'report/preview/audit.json')
               and f.name != 'delivery-manifest.json')
manifest = {f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
manifest_path = ROOT/'results/delivery-manifest.json'
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
files.append(manifest_path)
target = ROOT.parent/f'{STEM}.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file,file.relative_to(ROOT.parent).as_posix())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for name,digest in manifest.items():
        assert hashlib.sha256(archive.read('agent02/'+name)).hexdigest()==digest
print(target.name,'|',len(files),'files |',target.stat().st_size,'bytes')
