"""Four independent SQL cohorts, six model types, three initialization seeds."""
from pathlib import Path
import json
import platform
import shutil
import time
import numpy as np
import pandas as pd
import sklearn
import torch
from .database import database_path, sha256
from .datasets import load_prepared, prepare_database
from .metrics import metrics
from .schema import SCHEMAS, TASKS, LABELS
from .training import MODEL_IDS, MODEL_NAMES, NEURAL_IDS, train_one


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def save_run(root, output, dataset, model, record, val_score, test_score, arrays):
    model_id, seed = record['model_id'], record['seed']
    stem = model_id + '-seed' + str(seed)
    folder = output / dataset
    folder.mkdir(parents=True, exist_ok=True)
    weights = Path(root) / 'models/benchmark' / record['mode'] / dataset
    weights.mkdir(parents=True, exist_ok=True)
    if model_id in NEURAL_IDS:
        path = weights / (stem + '.pt')
        torch.save(model.state_dict(), path)
        record['weights'] = path.relative_to(root).as_posix()
        record['weights_sha256'] = sha256(path)
        record['artifact_bytes'] = path.stat().st_size
    elif model_id == 'logistic':
        path = weights / (stem + '.npz')
        np.savez_compressed(path, coef=model.coef_, intercept=model.intercept_, threshold=record['test']['threshold'])
        record['weights'] = path.relative_to(root).as_posix()
        record['weights_sha256'] = sha256(path)
        record['artifact_bytes'] = path.stat().st_size
    else:
        record['weights'] = None
        record['artifact_note'] = 'Tree ensemble not shipped; exact config/seed/data and held-out scores retained for refit.'
        record['artifact_bytes'] = None
    predictions = folder / (stem + '-predictions.npz')
    np.savez_compressed(predictions, y_val=arrays['y_val'], validation_score=val_score,
                        y_test=arrays['y_test'], test_score=test_score)
    record['prediction_file'] = predictions.relative_to(root).as_posix()
    record['prediction_sha256'] = sha256(predictions)
    write_json(folder / (stem + '.json'), record)


def promote_new_dataset(root, dataset, candidates, metadata):
    # Legacy serving artifacts are deliberately preserved, even when a new model scores better.
    if dataset in {'cdc', 'hospital'}:
        return None
    best = max((r for r in candidates if r['model_id'] in NEURAL_IDS),
               key=lambda r: r['validation']['roc_auc'])
    folder = Path(root) / 'models' / dataset
    folder.mkdir(parents=True, exist_ok=True)
    # Copy content only: Windows bind mounts may deny timestamp/permission updates.
    shutil.copyfile(Path(root) / best['weights'], folder / 'model.pt')
    meta = {'dataset': dataset, 'model_id': best['model_id'], 'model_name': best['model_name'],
        'model_version': '2.0-db-benchmark', 'feature_specs': SCHEMAS[dataset],
        'task': TASKS[dataset], 'label_semantics': LABELS[dataset],
        'preprocessing': metadata['preprocessing'], 'threshold': best['validation']['threshold'],
        'threshold_selection': 'maximum validation F1 only', 'seed': best['seed'],
        'best_epoch': best['best_epoch'], 'best_val_roc_auc': best['validation']['roc_auc'],
        'selection': 'best validation ROC-AUC among neural architectures/seeds; test excluded',
        'data_provenance': metadata, 'clinical_use': False,
        'score_semantics': 'Điểm sigmoid nghiên cứu; chưa hiệu chuẩn thành xác suất bệnh cá nhân tại Việt Nam.',
        'limitations': ['Cohort nhỏ, quần thể nước ngoài; chưa xác thực lâm sàng tại Việt Nam.',
            'Không dùng chẩn đoán, kê đơn hoặc thay quyết định bác sĩ.',
            'Split cố định; SD ba seed không bao gồm bất định chọn mẫu hoặc dịch chuyển miền.']}
    write_json(folder / 'metadata.json', meta)
    return {'dataset': dataset, 'model_id': best['model_id'], 'seed': best['seed'],
            'validation_roc_auc': best['validation']['roc_auc'], 'test_used_for_selection': False}


def summarize_runs(records):
    rows = []
    for record in records:
        row = {k: record[k] for k in ['dataset', 'model_id', 'model_name', 'seed', 'model_family',
                                     'train_and_evaluate_seconds', 'parameter_count']}
        row.update(record['test'])
        row.pop('confusion_matrix')
        row.pop('confusion_order')
        rows.append(row)
    table = pd.DataFrame(rows)
    columns = ['roc_auc', 'average_precision', 'f1', 'precision', 'sensitivity', 'specificity',
               'accuracy', 'brier', 'train_and_evaluate_seconds']
    summary = table.groupby(['dataset', 'model_id', 'model_name'])[columns].agg(['mean', 'std']).reset_index()
    summary.columns = ['_'.join(k).rstrip('_') if isinstance(k, tuple) else k for k in summary.columns]
    summary = summary.fillna(0.)
    return table, summary


def load_completed_run(root, output, dataset, model_id, seed, arrays, metadata):
    path = output / dataset / f'{model_id}-seed{seed}.json'
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding='utf-8'))
    assert record['dataset'] == dataset and record['model_id'] == model_id and record['seed'] == seed
    assert record['database_source']['raw_source_sha256'] == metadata['source_csv_sha256']
    predictions = Path(root) / record['prediction_file']
    assert sha256(predictions) == record['prediction_sha256']
    with np.load(predictions) as scores:
        np.testing.assert_array_equal(scores['y_val'], arrays['y_val'])
        np.testing.assert_array_equal(scores['y_test'], arrays['y_test'])
    if record['weights']:
        assert sha256(Path(root) / record['weights']) == record['weights_sha256']
    return record


def run_benchmark(root, mode='full', seeds=(42, 43, 44), prepare=True, resume=False):
    if mode not in {'full', 'smoke'} or not seeds:
        raise ValueError('Invalid benchmark mode/seeds')
    root = Path(root)
    output = root / 'results/benchmark' / mode
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    if prepare:
        prepare_database(root)
    records, promoted = [], []
    environment = {'python': platform.python_version(), 'torch': torch.__version__,
        'numpy': np.__version__, 'pandas': pd.__version__, 'sklearn': sklearn.__version__,
        'platform': platform.platform(), 'mode': mode, 'model_seeds': list(seeds), 'split_seed': 42}
    write_json(output / 'environment.json', environment)
    for dataset in SCHEMAS:
        # Actual SELECT supplies the arrays used by every following fit, never pre-existing NPZ caches.
        arrays, metadata = load_prepared(root, dataset)
        candidates = []
        for model_id in MODEL_IDS:
            for seed in seeds:
                previous = load_completed_run(root, output, dataset, model_id, seed, arrays, metadata) if resume else None
                if previous:
                    records.append(previous)
                    candidates.append(previous)
                    print('VERIFIED EXISTING RUN', dataset, model_id, seed, flush=True)
                    continue
                model, result, val_score, test_score = train_one(arrays, model_id, seed, mode)
                result.update(dataset=dataset, task=TASKS[dataset], label_semantics=LABELS[dataset],
                              database_source={'table': metadata['prepared_table'],
                                  'queries': metadata['training_queries'],
                                  'raw_source_sha256': metadata['source_csv_sha256']})
                save_run(root, output, dataset, model, result, val_score, test_score, arrays)
                records.append(result)
                candidates.append(result)
                print('BENCHMARK', dataset, model_id, seed,
                      'val_auc', round(result['validation']['roc_auc'], 5),
                      'test_auc', round(result['test']['roc_auc'], 5), flush=True)
                del model
        if mode == 'full':
            choice = promote_new_dataset(root, dataset, candidates, metadata)
            if choice:
                promoted.append(choice)
        baseline = metrics(arrays['y_test'], np.zeros(len(arrays['y_test'])), .5)
        write_json(output / dataset / 'always-negative-baseline.json', baseline)
    table, summary = summarize_runs(records)
    table.to_csv(output / 'runs.csv', index=False, encoding='utf-8-sig')
    summary.to_csv(output / 'summary.csv', index=False, encoding='utf-8-sig')
    result = {'environment': environment, 'dataset_count': len(SCHEMAS), 'model_types': MODEL_IDS,
        'model_type_count': len(MODEL_IDS), 'dataset_model_combinations': len(SCHEMAS) * len(MODEL_IDS),
        'run_count': len(records), 'elapsed_seconds': time.perf_counter() - started,
        'database_sha256': sha256(database_path(root)), 'active_new_models': promoted,
        'legacy_cdc_hospital_serving_artifacts_preserved': True, 'runs': records,
        'limitations': ['Different tasks/cohorts: compare model types within each dataset only.',
            'Three model seeds on one fixed split do not estimate population/generalization uncertainty.',
            'Early Stage duplicate feature vectors removed: 520 raw rows become 251 unique vectors.',
            'No posthoc calibration, Vietnam validation or clinical deployment claim.']}
    write_json(output / 'benchmark-results.json', result)
    return result
