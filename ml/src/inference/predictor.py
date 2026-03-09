import torch
from ml.src.models.gnn_model import UrbanGNN

_model_cache: UrbanGNN | None = None

def load_model(ckpt_path: str = "ml/checkpoints/best_model.pt",
               node_in=18, edge_in=4, hidden=64, heads=4, dropout=0.3) -> UrbanGNN:
    global _model_cache
    if _model_cache is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        m = UrbanGNN(node_in=node_in, edge_in=edge_in,
                     hidden=hidden, heads=heads, dropout=dropout)
        try:
            m.load_state_dict(torch.load(ckpt_path, map_location=device))
        except FileNotFoundError:
            print(f"[ML] No checkpoint at {ckpt_path}. Using untrained model.")
        m.eval()
        _model_cache = m.to(device)
    return _model_cache
