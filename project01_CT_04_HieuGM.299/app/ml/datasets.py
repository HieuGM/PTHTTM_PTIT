"""SQL-backed cohort preparation with immutable split membership and train-only statistics."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from .database import connect_database, ingest_database, read_source
from .schema import SCHEMAS

PIMA_MISSING = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']


def canonical_frame(source, dataset):
    frame = source.copy()
    names = [item['name'] for item in SCHEMAS[dataset]]
    counts = {'raw_rows': len(frame)}
    if dataset == 'hospital':
        counts['raw_patients'] = int(frame.patient_nbr.nunique())
        frame = frame.loc[frame.gender.isin(['Female', 'Male'])].copy()
        frame['AgeGroup'] = frame.age.str.extract(r'\[(\d+)-')[0].astype(int) // 10 + 1
        frame['Gender'] = frame.gender.map({'Female': 0, 'Male': 1})
        y = (frame.readmitted == '<30').astype(int)
        groups = frame.patient_nbr.to_numpy()
        counts['invalid_gender_rows_removed'] = counts['raw_rows'] - len(frame)
    else:
        if dataset == 'early':
            frame['Gender'] = frame.Gender.map({'Female': 0, 'Male': 1})
            for name in names[2:]:
                frame[name] = frame[name].map({'No': 0, 'Yes': 1})
            target = 'class'
            frame[target] = frame[target].map({'Negative': 0, 'Positive': 1})
        else:
            target = 'Diabetes_binary' if dataset == 'cdc' else 'Outcome'
        assert not frame[names + [target]].isna().any().any()
        counts['exact_duplicate_rows'] = int(frame.duplicated(subset=names + [target]).sum())
        hashes = pd.util.hash_pandas_object(frame[names], index=False)
        conflict = frame.groupby(hashes)[target].transform('nunique') > 1
        counts['conflicting_feature_rows_removed'] = int(conflict.sum())
        frame = frame.loc[~conflict].drop_duplicates(subset=names).reset_index(drop=True)
        y = frame[target].astype(int)
        groups = pd.util.hash_pandas_object(frame[names], index=False).astype(str).to_numpy()
    result = frame[names].astype(np.float64).reset_index(drop=True)
    result['target'] = y.to_numpy(dtype=np.int64)
    # The training tables never contain actual patient numbers.
    result['group_token'] = pd.util.hash_pandas_object(pd.Series(groups), index=False).astype(str)
    result['sample_id'] = np.arange(len(result))
    counts.update(clean_rows=len(result), features=names, group_unit='patient' if dataset == 'hospital' else 'unique feature vector')
    return result, counts


def assign_splits(frame, dataset):
    ids = np.arange(len(frame))
    y, groups = frame.target.to_numpy(), frame.group_token.to_numpy()
    if dataset == 'hospital':
        # Original patient IDs are only needed for the exact established group split.
        # group_token lexical ordering differs from patient number, so caller supplies ordered groups.
        groups = frame.attrs['original_groups']
        tr, remainder = next(GroupShuffleSplit(n_splits=1, test_size=.30, random_state=42).split(ids, y, groups))
        va, te = next(GroupShuffleSplit(n_splits=1, test_size=.50, random_state=43).split(remainder, y[remainder], groups[remainder]))
        parts = (tr, remainder[va], remainder[te])
    else:
        tr, remainder = train_test_split(ids, test_size=.30, random_state=42, stratify=y)
        va, te = train_test_split(remainder, test_size=.50, random_state=42, stratify=y[remainder])
        parts = (tr, va, te)
    tokens = [set(frame.iloc[p].group_token) for p in parts]
    assert not (tokens[0] & tokens[1] or tokens[0] & tokens[2] or tokens[1] & tokens[2])
    frame['split'] = ''
    frame['split_order'] = -1
    for label, part in zip(('train', 'val', 'test'), parts):
        frame.loc[part, 'split'] = label
        frame.loc[part, 'split_order'] = np.arange(len(part))
    return frame


def fit_statistics(frame, names, dataset):
    values = frame[names].to_numpy(dtype=np.float64)
    if dataset == 'pima':
        for name in PIMA_MISSING:
            values[values[:, names.index(name)] == 0, names.index(name)] = np.nan
    train = values[frame.split.to_numpy() == 'train']
    medians = np.nanmedian(train, axis=0)
    assert np.isfinite(medians).all()
    train = np.where(np.isnan(train), medians, train)
    mean, scale = train.mean(axis=0), train.std(axis=0)
    scale[scale < 1e-8] = 1
    return {'mean': mean.tolist(), 'scale': scale.tolist(), 'median': medians.tolist(),
            'zero_as_missing': PIMA_MISSING if dataset == 'pima' else [],
            'fitted_on': 'train rows only; validation/test excluded'}


def prepare_database(root):
    root = Path(root)
    sources = ingest_database(root)
    manifest = {}
    with connect_database(root) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS preparation(dataset TEXT PRIMARY KEY, metadata TEXT)')
    for dataset in SCHEMAS:
        source, query = read_source(root, dataset)
        frame, counts = canonical_frame(source, dataset)
        if dataset == 'hospital':
            frame.attrs['original_groups'] = source.loc[source.gender.isin(['Female', 'Male']), 'patient_nbr'].to_numpy()
        frame = assign_splits(frame, dataset)
        names = [item['name'] for item in SCHEMAS[dataset]]
        statistics = fit_statistics(frame, names, dataset)
        counts['split'] = {s: {'n': int((frame.split == s).sum()),
            'positive': int(frame.loc[frame.split == s, 'target'].sum()),
            'groups': int(frame.loc[frame.split == s, 'group_token'].nunique())} for s in ('train', 'val', 'test')}
        info = {**sources[dataset], **counts, 'source_query': query, 'split_seed': 42,
                'preprocessing': statistics, 'group_overlap': 0, 'database_used': True,
                'identifiers_in_features': False, 'prepared_table': 'prepared_' + dataset}
        with connect_database(root) as connection:
            frame.attrs = {}
            frame.to_sql(info['prepared_table'], connection, if_exists='replace', index=False, chunksize=2000)
            connection.execute('INSERT OR REPLACE INTO preparation VALUES (?,?)', (dataset, json.dumps(info)))
        manifest[dataset] = info
        print('SQL PREPARED', dataset, counts['split'], flush=True)
    folder = root / 'results/benchmark'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'database-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def load_prepared(root, dataset):
    if dataset not in SCHEMAS:
        raise ValueError('Unknown dataset')
    names = [item['name'] for item in SCHEMAS[dataset]]
    with connect_database(root) as connection:
        row = connection.execute('SELECT metadata FROM preparation WHERE dataset=?', (dataset,)).fetchone()
        if row is None:
            raise RuntimeError('Run prepare_database before benchmarking')
        metadata = json.loads(row[0])
        arrays, queries = {}, []
        for split in ('train', 'val', 'test'):
            query = f'SELECT * FROM "prepared_{dataset}" WHERE split=? ORDER BY split_order'
            frame = pd.read_sql_query(query, connection, params=(split,))
            raw = frame[names].to_numpy(dtype=np.float64)
            values = raw.copy()
            prep = metadata['preprocessing']
            for name in prep['zero_as_missing']:
                values[values[:, names.index(name)] == 0, names.index(name)] = np.nan
            values = np.where(np.isnan(values), np.asarray(prep['median']), values)
            arrays['x_' + split] = ((values - prep['mean']) / prep['scale']).astype(np.float32)
            arrays['raw_' + split] = raw.astype(np.float32)
            arrays['y_' + split] = frame.target.to_numpy(dtype=np.int64)
            queries.append({'sql': query, 'parameters': [split], 'rows': len(frame)})
    return arrays, {**metadata, 'training_queries': queries}
