"""Load local artifacts; validate complete requests before neural inference."""
import json
import math
from functools import lru_cache
from pathlib import Path
import numpy as np
import torch
from .network import RiskMLP

ROOT = Path(__file__).resolve().parents[2]


class Predictor:
    def __init__(self, project_root=None):
        self.root = Path(project_root) if project_root else ROOT
        self.loaded = {}

    def _load(self, dataset):
        if dataset not in {'cdc', 'hospital'}:
            raise ValueError('dataset phải là cdc hoặc hospital')
        if dataset not in self.loaded:
            folder = self.root / 'models' / dataset
            meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
            model = RiskMLP(len(meta['feature_specs']))
            model.load_state_dict(torch.load(folder / 'model.pt', map_location='cpu',
                                            weights_only=True))
            model.eval()
            self.loaded[dataset] = (model, meta)
        return self.loaded[dataset]

    def metadata(self, dataset):
        _, meta = self._load(dataset)
        return json.loads(json.dumps(meta))

    def predict(self, dataset, features):
        model, meta = self._load(dataset)
        if not isinstance(features, dict):
            raise ValueError('features phải là object')
        names = [item['name'] for item in meta['feature_specs']]
        missing = sorted(set(names) - set(features))
        extra = sorted(set(features) - set(names))
        if missing or extra:
            raise ValueError(f'Thiếu trường: {missing}; trường không hợp lệ: {extra}')
        values = []
        for item in meta['feature_specs']:
            value = features[item['name']]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{item['name']}: cần số thực hữu hạn")
            if not math.isfinite(value) or not item['min'] <= value <= item['max']:
                raise ValueError(f"{item['name']}: ngoài khoảng {item['min']}–{item['max']}")
            if item['integer'] and int(value) != value:
                raise ValueError(f"{item['name']}: cần số nguyên theo mã dữ liệu")
            values.append(value)
        scaler = meta['preprocessing']
        x = (np.asarray(values, dtype=np.float32) - scaler['mean']) / scaler['scale']
        with torch.inference_mode():
            score = float(torch.sigmoid(model(torch.tensor(x[None], dtype=torch.float32)))[0])
        return {'dataset': dataset, 'risk_score': score, 'threshold': meta['threshold'],
                'predicted_class': int(score >= meta['threshold']), 'task': meta['task'],
                'label_semantics': meta['label_semantics'], 'model_name': meta['model_name'],
                'clinical_use': False, 'score_semantics': meta['score_semantics'],
                'limitations': meta['limitations']}


@lru_cache(maxsize=1)
def _default():
    return Predictor()


def predict(dataset, features):
    return _default().predict(dataset, features)


def get_metadata(dataset):
    return _default().metadata(dataset)
