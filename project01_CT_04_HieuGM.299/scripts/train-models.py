"""Train both genuine datasets on CPU; checkpoints/thresholds from validation."""
import argparse
import copy
import importlib.util
import json
import platform
import random
import sys
import time
from pathlib import Path
import numpy as np
import sklearn
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.ml.network import RiskMLP
from app.ml.schema import LABELS, SCHEMAS, TASKS
module = importlib.util.spec_from_file_location('metrics', Path(__file__).with_name('model-metrics.py'))
mm = importlib.util.module_from_spec(module)
module.loader.exec_module(mm)


def scores(model, x):
    model.eval()
    with torch.inference_mode():
        return torch.sigmoid(model(torch.from_numpy(x))).numpy()


def train(dataset, epochs):
    start = time.perf_counter()
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(4)
    arrays = np.load(ROOT / f'data/splits/{dataset}.npz')
    xt, yt = arrays['x_train'], arrays['y_train']
    xv, yv = arrays['x_val'], arrays['y_val']
    xe, ye = arrays['x_test'], arrays['y_test']
    model = RiskMLP(xt.shape[1])
    optim = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = torch.nn.BCEWithLogitsLoss()
    x, y = torch.from_numpy(xt), torch.tensor(yt, dtype=torch.float32)
    best, best_epoch, history, state = -1, 0, [], None
    for epoch in range(1, epochs+1):
        model.train()
        order = torch.randperm(len(y))
        total = 0
        for ids in order.split(2048):
            optim.zero_grad()
            loss = criterion(model(x[ids]), y[ids])
            loss.backward()
            optim.step()
            total += float(loss.detach()) * len(ids)
        val_scores = scores(model, xv)
        auc = float(roc_auc_score(yv, val_scores))
        history.append({'epoch': epoch, 'train_bce': total/len(y), 'val_roc_auc': auc})
        if auc > best + 1e-5:
            best, best_epoch, state = auc, epoch, copy.deepcopy(model.state_dict())
        print(dataset, epoch, history[-1], flush=True)
        if epoch-best_epoch >= 5:
            break
    model.load_state_dict(state)
    threshold = mm.choose_threshold(yv, scores(model, xv))
    mlp_test = scores(model, xe)
    baseline = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    baseline.fit(xt, yt)
    logistic_threshold = mm.choose_threshold(yv, baseline.predict_proba(xv)[:, 1])
    logistic_test = baseline.predict_proba(xe)[:, 1]
    folder = ROOT / 'models' / dataset
    folder.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), folder / 'model.pt')
    manifest = json.loads((ROOT / 'results/data-manifest.json').read_text())
    meta = {'dataset': dataset, 'model_name': 'PyTorch MLP 64-32-16', 'task': TASKS[dataset],
            'label_semantics': LABELS[dataset], 'feature_specs': SCHEMAS[dataset],
            'preprocessing': {'mean': arrays['mean'].tolist(), 'scale': arrays['scale'].tolist()},
            'threshold': threshold, 'threshold_selection': 'Maximum F1 on validation only',
            'score_semantics': 'Điểm sigmoid của mô hình phân loại; chưa hiệu chỉnh/xác thực '
                               'thành xác suất bệnh cho cá nhân tại Việt Nam.',
            'limitations': ['Dữ liệu Hoa Kỳ lịch sử; chưa kiểm chứng trên bệnh nhân Việt Nam.',
                            'Không dùng để chẩn đoán, kê đơn hoặc thay quyết định bác sĩ.',
                            'Hai bộ dữ liệu có nhãn và quần thể khác nhau; không so trực tiếp AUC.'],
            'architecture': [xt.shape[1], 64, 32, 16, 1], 'seed': 42,
            'best_epoch': best_epoch, 'best_val_roc_auc': best,
            'data_provenance': manifest[dataset], 'clinical_use': False}
    if dataset == 'hospital':
        meta['limitations'].append('Đặc trưng chỉ đầy đủ lúc ra viện; không phải dự báo lúc nhập viện.')
    (folder / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    np.savez_compressed(folder / 'logistic-baseline.npz', coef=baseline.coef_, intercept=baseline.intercept_,
                        threshold=logistic_threshold)
    np.savez_compressed(ROOT / f'results/{dataset}-test-predictions.npz', y_true=ye,
                        mlp_score=mlp_test, logistic_score=logistic_test)
    result = {'dataset': dataset, 'task': TASKS[dataset], 'label_semantics': LABELS[dataset],
              'seed': 42, 'epochs_run': len(history), 'best_epoch': best_epoch,
              'best_val_roc_auc': best, 'history': history, 'test': {
                  'mlp': mm.metrics(ye, mlp_test, threshold),
                  'logistic': mm.metrics(ye, logistic_test, logistic_threshold),
                  'always_negative': mm.metrics(ye, np.zeros(len(ye)), 0.5)},
              'train_seconds': time.perf_counter()-start,
              'parameter_count': sum(p.numel() for p in model.parameters()),
              'protocol': {'checkpoint': 'Maximum validation ROC-AUC; patience=5',
                           'threshold': 'Maximum validation F1, frozen before test',
                           'optimizer': 'Adam lr=0.001, weight_decay=0.00001, batch=2048',
                           'test_used_in_training_or_selection': False,
                           'single_seed_limitation': True, 'posthoc_calibration': False}}
    (ROOT / f'results/{dataset}-training.json').write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                                       encoding='utf-8')
    print('FINISHED', dataset, json.dumps(result['test']), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', choices=['cdc', 'hospital', 'all'], default='all')
    parser.add_argument('--epochs', type=int, default=25)
    args = parser.parse_args()
    env = {'python': platform.python_version(), 'torch': torch.__version__,
           'numpy': np.__version__, 'sklearn': sklearn.__version__, 'platform': platform.platform()}
    (ROOT / 'results/environment.json').write_text(json.dumps(env, indent=2), encoding='utf-8')
    for dataset in ['cdc', 'hospital'] if args.dataset == 'all' else [args.dataset]:
        train(dataset, args.epochs)


if __name__ == '__main__':
    main()
