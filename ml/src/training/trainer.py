import os, json, torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.tensorboard import SummaryWriter
from torch_geometric.loader import DataLoader
from ml.src.models.gnn_model import UrbanGNN
from ml.src.training.loss import UrbanPlannerLoss
from ml.src.training.metrics import compute_metrics
from ml.src.training.early_stopping import EarlyStopping

def train(train_ds, val_ds, cfg: dict, ckpt_dir: str = "ml/checkpoints") -> UrbanGNN:
    device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model   = UrbanGNN(
        node_in=cfg["node_in_dim"], edge_in=cfg["edge_in_dim"],
        hidden=cfg["hidden_dim"], heads=cfg["num_heads"],
        dropout=cfg["dropout"],
    ).to(device)

    train_loader = DataLoader(train_ds, batch_size=cfg["batch_size"], shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=cfg["batch_size"])

    opt     = AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    sched   = CosineAnnealingLR(opt, T_max=cfg["epochs"], eta_min=1e-6)
    crit    = UrbanPlannerLoss()
    es      = EarlyStopping(patience=cfg["patience"])
    writer  = SummaryWriter("ml/logs/tensorboard")
    history = []
    os.makedirs(ckpt_dir, exist_ok=True)

    for epoch in range(1, cfg["epochs"] + 1):
        # ── Train ──
        model.train()
        t_loss = 0.0
        for batch in train_loader:
            batch = batch.to(device)
            opt.zero_grad()
            g_score, e_scores = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
            g_labels = batch.y[:batch.num_graphs] if batch.y.shape[0] >= batch.num_graphs else batch.y
            e_labels = batch.y
            loss, *_ = crit(g_score, e_scores, g_labels, e_labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            t_loss += loss.item()
        sched.step()

        # ── Validate ──
        model.eval()
        v_loss = 0.0; all_p, all_l = [], []
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                g_score, e_scores = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                g_labels = batch.y[:batch.num_graphs] if batch.y.shape[0] >= batch.num_graphs else batch.y
                e_labels = batch.y
                loss, *_ = crit(g_score, e_scores, g_labels, e_labels)
                v_loss += loss.item()
                all_p.extend(g_score.squeeze().cpu().tolist())
                all_l.extend(g_labels.cpu().tolist())

        atl = t_loss / len(train_loader)
        avl = v_loss / len(val_loader)
        mtr = compute_metrics(all_p, [int(l) for l in all_l])

        writer.add_scalar("Loss/Train", atl, epoch)
        writer.add_scalar("Loss/Val",   avl, epoch)
        for k, v in mtr.items():
            writer.add_scalar(f"Metrics/{k}", v, epoch)

        print(f"Epoch {epoch:03d} | TLoss={atl:.4f} | VLoss={avl:.4f} | "
              f"F1={mtr['f1']} | AUC={mtr['auc']}")
        history.append({"epoch": epoch, "train_loss": atl, "val_loss": avl, **mtr})

        if es.step(avl):
            print(f"  Early stop at epoch {epoch}")
            break
        if avl == es.best_score:
            torch.save(model.state_dict(), f"{ckpt_dir}/best_model.pt")
            print(f"  ✅ Best model saved")

    torch.save(model.state_dict(), f"{ckpt_dir}/last_epoch.pt")
    os.makedirs("ml/logs/training_runs", exist_ok=True)
    with open("ml/logs/training_runs/history.json", "w") as f:
        json.dump(history, f, indent=2)
    writer.close()
    return model
