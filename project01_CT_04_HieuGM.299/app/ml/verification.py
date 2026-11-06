"""Real SQL, checkpoint and prediction verification for the completed benchmark."""
from pathlib import Path
import json
import math
import numpy as np
import torch
from scipy.special import expit
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve
from .database import connect_database, sha256
from .datasets import load_prepared
from .network import build_model
from .predict import Predictor, validate_features
from .schema import SCHEMAS
from .training import NEURAL_IDS, MODEL_IDS


def verify_benchmark(root, mode='full'):
    root = Path(root)
    output = root / 'results/benchmark' / mode
    result = json.loads((output / 'benchmark-results.json').read_text(encoding='utf-8'))
    checks = []
    datasets = {}
    for dataset in SCHEMAS:
        arrays, metadata = load_prepared(root, dataset)
        datasets[dataset] = arrays
        names = metadata['features']
        raw = arrays['raw_train'].astype(np.float64)
        for name in metadata['preprocessing']['zero_as_missing']:
            raw[raw[:, names.index(name)] == 0, names.index(name)] = np.nan
        # Compare to true SQL float64 values, not rounded raw_train float32 snapshots.
        columns = ','.join('"'+name+'"' for name in names)
        with connect_database(root) as connection:
            values = connection.execute(f'SELECT {columns} FROM "prepared_{dataset}" WHERE split=? ORDER BY split_order', ('train',)).fetchall()
            training = np.asarray(values, dtype=np.float64)
            overlap = connection.execute(f'SELECT COUNT(*) FROM (SELECT group_token FROM "prepared_{dataset}" GROUP BY group_token HAVING COUNT(DISTINCT split)>1)').fetchone()[0]
        assert overlap == 0
        for name in metadata['preprocessing']['zero_as_missing']:
            training[training[:, names.index(name)] == 0, names.index(name)] = np.nan
        median = np.nanmedian(training, axis=0)
        training = np.where(np.isnan(training), median, training)
        np.testing.assert_allclose(median, metadata['preprocessing']['median'], atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(training.mean(axis=0), metadata['preprocessing']['mean'], atol=1e-11, rtol=1e-12)
        scale = training.std(axis=0)
        scale[scale < 1e-8] = 1
        np.testing.assert_allclose(scale, metadata['preprocessing']['scale'], atol=1e-11, rtol=1e-12)
        checks.append({'dataset': dataset, 'sql_group_disjoint_and_train_only_statistics': 'passed'})
    keys = {(r['dataset'], r['model_id'], r['seed']) for r in result['runs']}
    assert len(keys) == len(SCHEMAS)*len(MODEL_IDS)*len(result['environment']['model_seeds'])
    for record in result['runs']:
        arrays = datasets[record['dataset']]
        path = root / record['prediction_file']
        assert sha256(path) == record['prediction_sha256']
        with np.load(path) as predictions:
            np.testing.assert_array_equal(predictions['y_test'], arrays['y_test'])
            np.testing.assert_array_equal(predictions['y_val'], arrays['y_val'])
            score, validation = predictions['test_score'], predictions['validation_score']
            for labels, values, metrics in [(arrays['y_test'], score, record['test']),
                                             (arrays['y_val'], validation, record['validation'])]:
                assert np.isfinite(values).all() and ((values >= 0) & (values <= 1)).all()
                assert math.isclose(roc_auc_score(labels, values), metrics['roc_auc'], abs_tol=1e-14)
                assert math.isclose(average_precision_score(labels, values), metrics['average_precision'], abs_tol=1e-14)
            precision, recall, thresholds = precision_recall_curve(arrays['y_val'], validation)
            f1 = 2*precision[:-1]*recall[:-1]/np.maximum(precision[:-1]+recall[:-1], 1e-12)
            assert record['test']['threshold'] == float(thresholds[np.argmax(f1)])
            if record['model_id'] in NEURAL_IDS:
                model = build_model(arrays['x_train'].shape[1], record['model_id'])
                weights = root / record['weights']
                assert sha256(weights) == record['weights_sha256']
                model.load_state_dict(torch.load(weights, map_location='cpu', weights_only=True))
                model.eval()
                with torch.inference_mode():
                    fresh = torch.sigmoid(model(torch.from_numpy(arrays['x_test']))).numpy()
                np.testing.assert_array_equal(fresh, score)
            elif record['model_id'] == 'logistic':
                weights = np.load(root / record['weights'])
                logits = arrays['x_test'] @ weights['coef'].T + weights['intercept']
                # sklearn uses scipy.expit; preserve its float32 rounding convention.
                fresh = expit(logits.ravel())
                np.testing.assert_allclose(fresh, score, rtol=1e-13, atol=1e-13)
        checks.append({'dataset': record['dataset'], 'model_id': record['model_id'],
                       'seed': record['seed'], 'predictions_and_validation_threshold': 'passed'})
    predictor = Predictor(root)
    if mode == 'full':
        for dataset, specs in SCHEMAS.items():
            features = {s['name']: s['default'] for s in specs}
            response = predictor.predict(dataset, features)
            assert 0 <= response['risk_score'] <= 1 and response['clinical_use'] is False
            for invalid in [dict(features, unexpected=1), {k:v for k,v in features.items() if k != specs[0]['name']},
                            dict(features, **{specs[0]['name']: True}), dict(features, **{specs[0]['name']: float('nan')})]:
                try:
                    validate_features(dataset, invalid)
                except ValueError:
                    continue
                raise AssertionError('Invalid features accepted')
            checks.append({'dataset': dataset, 'real_serving_and_strict_schema': 'passed'})
    report = {'status': 'passed', 'checks_count': len(checks), 'run_count': len(keys), 'checks': checks}
    (output / 'model-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report
