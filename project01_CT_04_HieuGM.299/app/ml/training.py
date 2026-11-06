"""Six fixed model configurations; checkpoint and threshold selection exclude test."""
import copy
import random
import time
import numpy as np
import torch
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from .metrics import choose_threshold, metrics
from .network import build_model

MODEL_IDS = ['logistic', 'random_forest', 'hist_gradient_boosting', 'mlp2', 'mlp3', 'resmlp']
NEURAL_IDS = ['mlp2', 'mlp3', 'resmlp']
MODEL_NAMES = {'logistic': 'Logistic Regression', 'random_forest': 'Random Forest',
    'hist_gradient_boosting': 'Histogram Gradient Boosting', 'mlp2': 'MLP 64-32',
    'mlp3': 'MLP 64-32-16', 'resmlp': 'Residual MLP width32, two residual blocks'}


def neural_scores(model, x):
    model.eval()
    with torch.inference_mode():
        return torch.sigmoid(model(torch.from_numpy(x))).numpy()


def fit_neural(arrays, model_id, seed, mode):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(2)
    xt, yt, xv, yv = [arrays[k] for k in ('x_train', 'y_train', 'x_val', 'y_val')]
    large = len(yt) > 10000
    epochs = (25 if large else 100) if mode == 'full' else 2
    batch = 2048 if large else 32
    model = build_model(xt.shape[1], model_id)
    optimizer = torch.optim.Adam(model.parameters(), lr=.001, weight_decay=1e-5)
    criterion = torch.nn.BCEWithLogitsLoss()
    x, y = torch.from_numpy(xt), torch.tensor(yt, dtype=torch.float32)
    best_auc, best_epoch, best_state, history = -1., 0, None, []
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.
        for ids in torch.randperm(len(y)).split(batch):
            optimizer.zero_grad()
            loss = criterion(model(x[ids]), y[ids])
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(ids)
        auc = float(roc_auc_score(yv, neural_scores(model, xv)))
        history.append({'epoch': epoch, 'train_bce': total/len(y), 'val_roc_auc': auc})
        if auc > best_auc + 1e-5:
            best_auc, best_epoch, best_state = auc, epoch, copy.deepcopy(model.state_dict())
        if epoch - best_epoch >= 10:
            break
    model.load_state_dict(best_state)
    config = {'optimizer': 'Adam', 'learning_rate': .001, 'weight_decay': 1e-5,
              'batch_size': batch, 'epochs_max': epochs, 'patience': 10,
              'checkpoint': 'maximum validation ROC-AUC; delta > 1e-5'}
    return model, history, best_epoch, config


def fit_classic(arrays, model_id, seed, mode):
    configs = {
        'logistic': dict(C=1., max_iter=1000, random_state=seed),
        'random_forest': dict(n_estimators=100 if mode == 'full' else 10, max_depth=12,
                             min_samples_leaf=5, n_jobs=2, random_state=seed),
        'hist_gradient_boosting': dict(max_iter=100 if mode == 'full' else 10, max_depth=6,
                                      early_stopping=False, random_state=seed)}
    classes = {'logistic': LogisticRegression, 'random_forest': RandomForestClassifier,
               'hist_gradient_boosting': HistGradientBoostingClassifier}
    model = classes[model_id](**configs[model_id])
    model.fit(arrays['x_train'], arrays['y_train'])
    return model, [], None, configs[model_id]


def train_one(arrays, model_id, seed, mode='full'):
    if mode not in {'full', 'smoke'} or model_id not in MODEL_IDS:
        raise ValueError('Invalid benchmark mode/model')
    started = time.perf_counter()
    neural = model_id in NEURAL_IDS
    if neural:
        model, history, best_epoch, config = fit_neural(arrays, model_id, seed, mode)
        score = lambda x: neural_scores(model, x)
        parameters = int(sum(p.numel() for p in model.parameters()))
    else:
        model, history, best_epoch, config = fit_classic(arrays, model_id, seed, mode)
        score = lambda x: model.predict_proba(x)[:, 1]
        parameters = None
    validation_score = score(arrays['x_val'])
    threshold = choose_threshold(arrays['y_val'], validation_score)
    # The test prediction is computed only after training/checkpoint/threshold selection.
    test_score = score(arrays['x_test'])
    result = {'model_id': model_id, 'model_name': MODEL_NAMES[model_id], 'seed': seed,
        'mode': mode, 'model_family': 'deep_learning' if neural else 'classical_ml',
        'config': config, 'history': history, 'best_epoch': best_epoch,
        'epochs_run': len(history) if neural else None, 'parameter_count': parameters,
        'validation': metrics(arrays['y_val'], validation_score, threshold),
        'test': metrics(arrays['y_test'], test_score, threshold),
        'threshold_selection': 'maximum F1 on validation only, frozen before test',
        'test_used_for_fit_checkpoint_threshold_or_serving_selection': False,
        'train_and_evaluate_seconds': time.perf_counter() - started}
    return model, result, validation_score, test_score
