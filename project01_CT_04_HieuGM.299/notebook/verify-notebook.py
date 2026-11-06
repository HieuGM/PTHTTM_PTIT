"""Execute only the ipynb from a fresh directory, no application source beside it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import nbformat
from nbclient import NotebookClient

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=['smoke','full'], required=True)
parser.add_argument('--directory', type=Path, required=True)
parser.add_argument('--source-cache', type=Path,
    help='Optional verified raw CSV cache; no application source is copied.')
args = parser.parse_args()
source = Path(__file__).with_name('project01-diacare.ipynb')
directory = args.directory.resolve()
directory.mkdir(parents=True, exist_ok=False)
target = directory/source.name
shutil.copyfile(source, target)
cache_manifest = {}
if args.source_cache:
    raw = directory/'diacare-notebook-output/data/raw'
    raw.mkdir(parents=True)
    for name in ('cdc.csv','hospital.csv','pima.csv','early.csv','pima-source.arff','early-source.zip'):
        cached = args.source_cache/name
        if cached.is_file():
            shutil.copyfile(cached, raw/name)
            cache_manifest[name] = hashlib.sha256(cached.read_bytes()).hexdigest()
os.environ['DIACARE_RUN_MODE'] = args.mode
os.environ.pop('DIACARE_NOTEBOOK_OUTPUT', None)
# Fresh kernel receives no provider/database credentials from the verification process.
for name in list(os.environ):
    if name.startswith(('FPT_', 'NEO4J_')):
        os.environ.pop(name)
notebook = nbformat.read(target, as_version=4)
started = time.perf_counter()


def complete(cell, cell_index, **kwargs):
    print('CELL', cell_index, cell.cell_type, round(time.perf_counter()-started, 2), flush=True)


client = NotebookClient(notebook, timeout=1800, kernel_name='python3',
    resources={'metadata':{'path':str(directory)}}, on_cell_complete=complete)
try:
    client.execute()
finally:
    nbformat.write(notebook, target)
summary = json.loads((directory/'diacare-notebook-output/results/notebook-validation.json').read_text())
summary.update(elapsed_seconds=time.perf_counter()-started,
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    source_files_present=[str(p.relative_to(directory)) for p in directory.rglob('*.py')],
    raw_source_cache=cache_manifest,
    executed_notebook=str(target), code_cells=sum(c.cell_type=='code' for c in notebook.cells))
(directory/'verification.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k != 'checks'}, ensure_ascii=False))
