"""Validation threshold choice and held-out binary metrics shared by all algorithms."""
import numpy as np
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix,
    precision_recall_curve, roc_auc_score, precision_score, recall_score, f1_score)


def choose_threshold(y, score):
    precision, recall, thresholds = precision_recall_curve(y, score)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
    return float(thresholds[int(np.argmax(f1))])


def metrics(y, score, threshold):
    pred = score >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel().tolist()
    return {'n': len(y), 'positive': int(y.sum()), 'prevalence': float(y.mean()),
        'threshold': float(threshold), 'roc_auc': float(roc_auc_score(y, score)),
        'average_precision': float(average_precision_score(y, score)),
        'f1': float(f1_score(y, pred, zero_division=0)),
        'precision': float(precision_score(y, pred, zero_division=0)),
        'sensitivity': float(recall_score(y, pred, zero_division=0)),
        'specificity': tn / max(tn+fp, 1), 'accuracy': (tn+tp)/len(y),
        'brier': float(brier_score_loss(y, score)), 'confusion_matrix': [[tn, fp], [fn, tp]],
        'confusion_order': 'rows=true0/1; columns=predicted0/1'}
