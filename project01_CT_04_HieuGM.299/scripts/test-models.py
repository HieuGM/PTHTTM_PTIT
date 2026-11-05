"""Real artifact checks: split/scaler integrity, prediction parity and bad inputs."""
import json
import sys
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.predict import Predictor


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('Invalid input accepted')


def main():
    torch.set_num_threads(2)
    predictor = Predictor(ROOT)
    records = {}
    for dataset in ['cdc', 'hospital']:
        meta = predictor.metadata(dataset)
        arrays = np.load(ROOT / f'data/splits/{dataset}.npz')
        raw = arrays['raw_train']
        np.testing.assert_allclose(arrays['mean'], raw.mean(axis=0, dtype=np.float64), atol=1e-10)
        np.testing.assert_allclose(arrays['scale'], raw.std(axis=0, dtype=np.float64), atol=1e-10)
        fields = meta['feature_specs']
        example = {s['name']: s['default'] for s in fields}
        output = predictor.predict(dataset, example)
        assert 0 <= output['risk_score'] <= 1 and output['clinical_use'] is False
        assert output['predicted_class'] == int(output['risk_score'] >= meta['threshold'])
        # Compare deployed scalar inference against saved untouched test score rows.
        scores = np.load(ROOT / f'results/{dataset}-test-predictions.npz')
        for i in range(30):
            features = {s['name']: float(value) for s, value in zip(fields, arrays['raw_test'][i])}
            predicted = predictor.predict(dataset, features)['risk_score']
            np.testing.assert_allclose(predicted, scores['mlp_score'][i], rtol=1e-5, atol=1e-6)
        reject(lambda: predictor.predict(dataset, {}))
        reject(lambda: predictor.predict(dataset, {**example, 'unexpected': 1}))
        first = fields[0]['name']
        for invalid in [None, '1', True, float('nan'), float('inf'),
                        fields[0]['min']-1, fields[0]['max']+1, 0.5]:
            reject(lambda bad=invalid: predictor.predict(dataset, {**example, first: bad}))
        # Metadata must not be mutable through caller aliases.
        copied = predictor.metadata(dataset)
        copied['threshold'] = -1
        assert predictor.metadata(dataset)['threshold'] >= 0
        assert meta['data_provenance']['group_overlap'] == 0
        assert set(scores.files) == {'y_true', 'mlp_score', 'logistic_score'}
        result = json.loads((ROOT / f'results/{dataset}-training.json').read_text(encoding='utf-8'))
        for model in result['test'].values():
            assert sum(sum(row) for row in model['confusion_matrix']) == model['n']
        assert result['protocol']['test_used_in_training_or_selection'] is False
        records[dataset] = {'status': 'passed', 'test_score_parity_rows': 30,
                            'scaler_train_only': True, 'invalid_input_cases': 10,
                            'clinical_use': False, 'group_overlap': 0}
    reject(lambda: predictor.predict('unknown', {}))
    out = ROOT / 'results/model-tests.json'
    out.write_text(json.dumps({'datasets': records, 'status': 'passed'}, indent=2), encoding='utf-8')
    print(out.read_text())


if __name__ == '__main__':
    main()
