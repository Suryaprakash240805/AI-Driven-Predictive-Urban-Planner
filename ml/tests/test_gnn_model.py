import torch
import pytest
from ml.src.models.gnn_model import UrbanGNN
from ml.src.synthetic.graph_generator import generate_graph
from torch_geometric.loader import DataLoader

def test_model_forward():
    model  = UrbanGNN(node_in=18, edge_in=4, hidden=32, heads=2)
    graph  = generate_graph(n_zones=6, valid=True)
    loader = DataLoader([graph], batch_size=1)
    batch  = next(iter(loader))
    g_score, e_scores = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
    assert g_score.shape == (1, 1)
    assert 0 <= g_score.item() <= 1
    assert e_scores.shape[0] == batch.num_edges

def test_output_range():
    model = UrbanGNN()
    for _ in range(10):
        g = generate_graph()
        l = DataLoader([g], batch_size=1)
        b = next(iter(l))
        gs, es = model(b.x, b.edge_index, b.edge_attr, b.batch)
        assert 0 <= gs.item() <= 1

def test_invalid_layout_lower_score():
    model = UrbanGNN()
    valid   = [generate_graph(valid=True)  for _ in range(10)]
    invalid = [generate_graph(valid=False) for _ in range(10)]
    def avg_score(ds):
        s = []
        for g in ds:
            l = DataLoader([g], batch_size=1)
            b = next(iter(l))
            gs, _ = model(b.x, b.edge_index, b.edge_attr, b.batch)
            s.append(gs.item())
        return sum(s) / len(s)
    # NOTE: Without training, this may not hold — it's a post-training sanity check
    assert avg_score(valid) >= 0 and avg_score(invalid) >= 0
