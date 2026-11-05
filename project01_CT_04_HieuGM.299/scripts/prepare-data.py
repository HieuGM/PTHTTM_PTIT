"""Pre-split leakage controls, patient disjointness, and train-only scaling."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.schema import SCHEMAS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cdc():
    source = ROOT / 'data/raw/cdc.csv'
    frame = pd.read_csv(source)
    # UCI exports may expose the original Kaggle target with the same name.
    names = [s['name'] for s in SCHEMAS['cdc']]
    counts = {'raw_rows': len(frame), 'exact_duplicate_rows':
              int(frame.duplicated(subset=names+['Diabetes_binary']).sum())}
    # Exclude conflicting target groups rather than arbitrarily selecting one label.
    hashes = pd.util.hash_pandas_object(frame[names], index=False)
    conflicts = frame.groupby(hashes)['Diabetes_binary'].transform('nunique') > 1
    counts['conflicting_feature_rows_removed'] = int(conflicts.sum())
    frame = frame.loc[~conflicts].drop_duplicates(subset=names).reset_index(drop=True)
    counts['clean_rows'] = len(frame)
    x = frame[names].to_numpy(dtype=np.float32)
    y = frame['Diabetes_binary'].to_numpy(dtype=np.int64)
    ids = np.arange(len(frame))
    tr, rem = train_test_split(ids, test_size=0.30, random_state=42, stratify=y)
    va, te = train_test_split(rem, test_size=0.50, random_state=42, stratify=y[rem])
    group_values = pd.util.hash_pandas_object(frame[names], index=False).to_numpy()
    return x, y, (tr, va, te), group_values, counts, source


def hospital():
    source = ROOT / 'data/raw/hospital.csv'
    frame = pd.read_csv(source, low_memory=False)
    counts = {'raw_rows': len(frame), 'raw_patients': int(frame['patient_nbr'].nunique())}
    frame = frame.loc[frame['gender'].isin(['Female', 'Male'])].copy()
    frame['AgeGroup'] = frame['age'].str.extract(r'\[(\d+)-')[0].astype(int) // 10 + 1
    frame['Gender'] = frame['gender'].map({'Female': 0, 'Male': 1})
    names = [s['name'] for s in SCHEMAS['hospital']]
    x = frame[names].to_numpy(dtype=np.float32)
    y = (frame['readmitted'] == '<30').to_numpy(dtype=np.int64)
    groups = frame['patient_nbr'].to_numpy()
    outer = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
    tr, rem = next(outer.split(x, y, groups))
    inner = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=43)
    va_i, te_i = next(inner.split(x[rem], y[rem], groups[rem]))
    counts.update(clean_rows=len(frame), invalid_gender_rows_removed=counts['raw_rows']-len(frame))
    return x, y, (tr, rem[va_i], rem[te_i]), groups, counts, source


def main():
    out = ROOT / 'data/splits'
    out.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for dataset, loader in [('cdc', cdc), ('hospital', hospital)]:
        x, y, splits, groups, counts, source = loader()
        tr, va, te = splits
        assert np.isfinite(x).all() and set(np.unique(y)) == {0, 1}
        sets = [set(groups[s].tolist()) for s in splits]
        assert not (sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])
        mean = x[tr].mean(axis=0, dtype=np.float64)
        scale = x[tr].std(axis=0, dtype=np.float64)
        scale[scale < 1e-8] = 1
        arrays = {'mean': mean, 'scale': scale}
        for label, split in zip(('train', 'val', 'test'), splits):
            arrays[f'x_{label}'] = ((x[split] - mean) / scale).astype(np.float32)
            arrays[f'y_{label}'] = y[split]
            arrays[f'raw_{label}'] = x[split]
        path = out / f'{dataset}.npz'
        np.savez_compressed(path, **arrays)
        counts['split'] = {label: {'n': len(s), 'positive': int(y[s].sum()),
                                  'groups': len(g)}
                           for label, s, g in zip(('train', 'val', 'test'), splits, sets)}
        counts.update(dataset=dataset, seed=42, group_overlap=0,
                      feature_names=[s['name'] for s in SCHEMAS[dataset]],
                      source_sha256=digest(source), split_sha256=digest(path),
                      scaling='mean/std fitted only on train; no imputation needed',
                      split_unit='unique feature vector' if dataset == 'cdc' else 'patient_nbr',
                      raw_identifiers_exported=False)
        counts['source_url'] = ('https://archive.ics.uci.edu/static/public/891/data.csv'
                                if dataset == 'cdc' else
                                'https://archive.ics.uci.edu/static/public/296/data.csv')
        counts['license'] = 'Kaggle original: CC0 Public Domain' if dataset == 'cdc' else 'CC BY 4.0'
        counts['download_or_verified_date'] = '2026-11-05'
        if dataset == 'cdc' and (ROOT / 'data/raw/cdc-uci.csv').exists():
            uci = pd.read_csv(ROOT / 'data/raw/cdc-uci.csv').drop(columns=['ID'], errors='ignore')
            local = pd.read_csv(source)
            equivalent = local.equals(uci.astype(local.dtypes.to_dict()))
            assert equivalent, 'Cached CDC differs from official UCI CSV'
            counts['uci_value_equivalence_verified'] = True
            counts['uci_csv_sha256'] = digest(ROOT / 'data/raw/cdc-uci.csv')
        manifest[dataset] = counts
        print(dataset, json.dumps(counts['split']), flush=True)
    (ROOT / 'results/data-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
