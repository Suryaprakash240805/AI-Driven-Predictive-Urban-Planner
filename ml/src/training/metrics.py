from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score
import torch

def compute_metrics(probs: list, labels: list) -> dict:
    preds = [1 if p > 0.5 else 0 for p in probs]
    return {
        "f1":        round(f1_score(labels, preds, zero_division=0), 4),
        "auc":       round(roc_auc_score(labels, probs), 4),
        "precision": round(precision_score(labels, preds, zero_division=0), 4),
        "recall":    round(recall_score(labels, preds, zero_division=0), 4),
        "accuracy":  round(sum(p==l for p,l in zip(preds,labels))/len(labels), 4),
    }
