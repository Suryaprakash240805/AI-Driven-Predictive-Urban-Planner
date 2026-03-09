import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_curve, roc_auc_score)
from torch_geometric.loader import DataLoader
from ml.src.training.metrics import compute_metrics

def evaluate(model, test_ds, device, batch_size=32) -> dict:
    loader = DataLoader(test_ds, batch_size=batch_size)
    model.eval()
    all_p, all_l, nbc_c, nbc_t = [], [], 0, 0

    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            g_score, e_scores = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
            g_labels = batch.y[:batch.num_graphs]
            e_labels = batch.y
            all_p.extend(g_score.squeeze().cpu().tolist())
            all_l.extend(g_labels.cpu().tolist())
            ep = (e_scores.squeeze() > 0.5).long().cpu()
            el = e_labels.long().cpu()
            nbc_c += (ep == el).sum().item()
            nbc_t += len(el)

    labels_int = [int(l) for l in all_l]
    mtr = compute_metrics(all_p, labels_int)
    mtr["nbc_compliance_acc"] = round(nbc_c / nbc_t * 100, 2) if nbc_t else 0

    print("\n" + "="*55)
    print("  TEST EVALUATION RESULTS")
    print("="*55)
    preds_bin = [1 if p > 0.5 else 0 for p in all_p]
    print(classification_report(labels_int, preds_bin,
                                  target_names=["Invalid","Valid"]))
    print(f"  NBC Compliance Detection: {mtr['nbc_compliance_acc']}%")

    _plot_results(labels_int, all_p, preds_bin)
    return mtr

def _plot_results(labels, probs, preds):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    # Confusion Matrix
    cm = confusion_matrix(labels, preds)
    axes[0].imshow(cm, cmap="Blues")
    axes[0].set_title("Confusion Matrix")
    axes[0].set_xticks([0,1]); axes[0].set_yticks([0,1])
    axes[0].set_xticklabels(["Invalid","Valid"])
    axes[0].set_yticklabels(["Invalid","Valid"])
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, cm[i,j], ha="center", va="center", fontsize=14)
    # ROC
    fpr, tpr, _ = roc_curve(labels, probs)
    auc = roc_auc_score(labels, probs)
    axes[1].plot(fpr, tpr, label=f"AUC={auc:.3f}", color="#D4AF37", lw=2)
    axes[1].plot([0,1],[0,1],"k--",lw=1)
    axes[1].set_xlabel("FPR"); axes[1].set_ylabel("TPR")
    axes[1].set_title("ROC Curve"); axes[1].legend()
    plt.tight_layout()
    plt.savefig("ml/logs/evaluation_results.png", dpi=150)
    plt.close()
