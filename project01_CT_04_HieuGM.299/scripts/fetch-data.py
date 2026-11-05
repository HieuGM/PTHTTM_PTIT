"""Fetch authentic public datasets; raw hospital IDs stay in ignored local raw/."""
import hashlib
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
URLS = {'cdc': 'https://archive.ics.uci.edu/static/public/891/data.csv',
        'hospital': 'https://archive.ics.uci.edu/static/public/296/data.csv'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        target = RAW / f'{name}.csv'
        if not target.exists():
            local = ROOT.parent / 'tieuluan01/chuong2-ml/data/cdc_diabetes_binary.csv'
            if name == 'cdc' and local.exists():
                shutil.copy2(local, target)
            else:
                with urllib.request.urlopen(url, timeout=120) as response:
                    target.write_bytes(response.read())
        print(name, target.stat().st_size, sha(target))


if __name__ == '__main__':
    main()
