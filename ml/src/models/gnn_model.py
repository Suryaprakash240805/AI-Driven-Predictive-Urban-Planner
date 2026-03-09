import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import (GATv2Conv, SAGEConv,
                                  global_mean_pool, global_max_pool, BatchNorm)

class ZoneEncoder(nn.Module):
    def __init__(self, in_dim: int, hidden: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
        )
    def forward(self, x): return self.net(x)

class UrbanGNN(nn.Module):
    """
    Hybrid GATv2 + GraphSAGE model.
    Input  → ZoneEncoder (18→64) → GATv2×2 → SAGEConv → Pool → MLP
    Output → graph_score (0-1 feasibility), edge_scores (per-edge NBC)
    """
    def __init__(self, node_in=18, edge_in=4, hidden=64,
                 heads=4, dropout=0.3):
        super().__init__()
        self.dropout = dropout
        self.encoder = ZoneEncoder(node_in, hidden)

        self.gat1 = GATv2Conv(hidden, hidden, heads=heads,
                               edge_dim=edge_in, concat=True, dropout=dropout)
        self.bn1  = BatchNorm(hidden * heads)

        self.gat2 = GATv2Conv(hidden * heads, hidden, heads=heads,
                               edge_dim=edge_in, concat=False, dropout=dropout)
        self.bn2  = BatchNorm(hidden)

        self.sage = SAGEConv(hidden, hidden)
        self.bn3  = BatchNorm(hidden)

        self.graph_head = nn.Sequential(
            nn.Linear(hidden * 2, hidden), nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 32), nn.ReLU(),
            nn.Linear(32, 1),
        )
        self.edge_head = nn.Sequential(
            nn.Linear(hidden * 2 + edge_in, 32),
            nn.ReLU(), nn.Linear(32, 1),
        )

    def forward(self, x, edge_index, edge_attr, batch):
        h = self.encoder(x)

        h = self.gat1(h, edge_index, edge_attr)
        h = self.bn1(h); h = F.elu(h)
        h = F.dropout(h, p=self.dropout, training=self.training)

        h = self.gat2(h, edge_index, edge_attr)
        h = self.bn2(h); h = F.elu(h)

        h = self.sage(h, edge_index)
        h = self.bn3(h); h = F.relu(h)

        h_pool = torch.cat([global_mean_pool(h, batch),
                             global_max_pool(h, batch)], dim=-1)
        graph_score = torch.sigmoid(self.graph_head(h_pool))

        src, dst = edge_index
        e_feats   = torch.cat([h[src], h[dst], edge_attr], dim=-1)
        edge_scores = torch.sigmoid(self.edge_head(e_feats))

        return graph_score, edge_scores
