"""Authentic CSV ingestion and a local SQLite database used by every benchmark fit."""
from contextlib import contextmanager, closing
from pathlib import Path
import hashlib
import io
import json
import sqlite3
import time
import urllib.error
import urllib.request
import zipfile
import numpy as np
import pandas as pd
from scipy.io import arff
from .schema import SCHEMAS

SOURCE_URLS = {
    'cdc': 'https://archive.ics.uci.edu/static/public/891/data.csv',
    'hospital': 'https://archive.ics.uci.edu/static/public/296/data.csv',
    'pima': 'https://openml.org/data/v1/download/37/diabetes.arff',
    'early': 'https://archive.ics.uci.edu/static/public/529/early+stage+diabetes+risk+prediction+dataset.zip'}
LICENSES = {'cdc': 'Kaggle original: CC0 Public Domain', 'hospital': 'CC BY 4.0',
            'pima': 'OpenML37 metadata licence: Public; original NIDDK/UCI provenance', 'early': 'CC BY 4.0'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def database_path(root):
    return Path(root) / 'data/database/diabetes.sqlite3'


@contextmanager
def connect_database(root):
    path = database_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise


def download_bytes(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'DiaCare-academic-project/2.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code < 500 and error.code != 429:
                raise
            if attempt == 2:
                raise
            print('Transient source download failure; retry', attempt+1, flush=True)
            time.sleep(2 ** attempt)


def fetch_sources(root):
    root = Path(root)
    raw = root / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    for dataset, url in SOURCE_URLS.items():
        target = raw / (dataset + '.csv')
        if target.exists():
            continue
        if dataset in {'cdc', 'hospital'}:
            target.write_bytes(download_bytes(url))
        elif dataset == 'pima':
            original = raw / 'pima-source.arff'
            original.write_bytes(download_bytes(url))
            records, _ = arff.loadarff(io.StringIO(original.read_text(encoding='utf-8')))
            frame = pd.DataFrame(records)
            labels = frame.iloc[:, -1].map({b'tested_negative': 0, b'tested_positive': 1})
            assert len(frame) == 768 and not labels.isna().any()
            result = frame.iloc[:, :8].astype(float)
            result.columns = [item['name'] for item in SCHEMAS['pima']]
            result['Outcome'] = labels.astype(int)
            result.to_csv(target, index=False, float_format='%.12g')
        else:
            archive = raw / 'early-source.zip'
            archive.write_bytes(download_bytes(url))
            with zipfile.ZipFile(archive) as zipped:
                target.write_bytes(zipped.read('diabetes_data_upload.csv'))
    return raw


def ingest_database(root):
    """Write real source rows first; downstream preparation reads these SQL tables."""
    raw = fetch_sources(root)
    manifest = {}
    with connect_database(root) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS source_info(dataset TEXT PRIMARY KEY, metadata TEXT)')
        for dataset in SCHEMAS:
            path = raw / (dataset + '.csv')
            frame = pd.read_csv(path, low_memory=False)
            frame.to_sql('raw_' + dataset, connection, if_exists='replace', index=False, chunksize=2000)
            info = {'dataset': dataset, 'source_url': SOURCE_URLS[dataset], 'license': LICENSES[dataset],
                    'raw_rows': len(frame), 'raw_columns': list(frame.columns),
                    'source_csv_sha256': sha256(path), 'raw_table': 'raw_' + dataset}
            connection.execute('INSERT OR REPLACE INTO source_info VALUES (?,?)',
                               (dataset, json.dumps(info, ensure_ascii=False)))
            manifest[dataset] = info
    return manifest


def read_source(root, dataset):
    if dataset not in SCHEMAS:
        raise ValueError('Unknown dataset')
    query = f'SELECT * FROM "raw_{dataset}" ORDER BY rowid'
    with connect_database(root) as connection:
        frame = pd.read_sql_query(query, connection)
    return frame, query
