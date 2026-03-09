import random
import torch
import numpy as np
import networkx as nx
from torch_geometric.utils import from_networkx
from torch_geometric.data import Data
from ml.src.synthetic.nbc_rules import is_adjacent_valid

ZONE_DIST = {
    "residential": ["residential"]*4 + ["green_space"]*2 + ["road","parking","setback"],
    "commercial":  ["commercial"]*3 + ["parking"]*2 + ["road"]*2 + ["green_space","utility"],
    "mixed":       ["residential"]*2 + ["commercial"]*2 + ["green_space","road","parking","utility","setback"],
}

def _node_feats(ztype: str) -> list:
    one_hot = [0.0]*8
    TYPE_IDX = {"residential":0,"commercial":1,"green_space":2,"road":3,
                "parking":4,"utility":5,"setback":6,"industrial":7}
    one_hot[TYPE_IDX.get(ztype, 0)] = 1.0
    return one_hot + [
        random.uniform(50, 5000) / 10000,
        random.uniform(0.4, 0.8) if ztype == "green_space" else random.uniform(0, 0.2),
        random.uniform(0.3, 0.9) if ztype in ["residential","commercial"] else 0.1,
        random.uniform(100, 5000) / 1000,
        random.uniform(200, 600) / 100,
        random.uniform(0, 15) / 45,
        random.choice([0, 0, 0, 1]),
        random.uniform(2, 30) / 50,
        0.0,
    ]

def generate_graph(n_zones: int = 8, use_type: str = "residential",
                   valid: bool = True) -> Data:
    zones = (ZONE_DIST.get(use_type, ZONE_DIST["residential"])[:n_zones]
             + [ZONE_DIST["residential"][0]] * max(0, n_zones - len(ZONE_DIST.get(use_type,[]))))
    zones = zones[:n_zones]

    if not valid:
        for k, z in enumerate(zones):
            if z == "green_space":
                zones[k] = "industrial"; break

    G = nx.Graph()
    for i, zt in enumerate(zones):
        G.add_node(i, x=_node_feats(zt))

    for i in range(n_zones - 1):
        compat = 1 if is_adjacent_valid(zones[i], zones[i+1]) else 0
        G.add_edge(i, i+1,
            edge_attr=[random.uniform(5,50)/100, random.uniform(10,200)/1000,
                       random.choice([6,9,12])/15, float(compat)],
            y=float(compat))

    data = from_networkx(G)
    if not hasattr(data, "edge_attr") or data.edge_attr is None:
        data.edge_attr = torch.zeros(data.num_edges, 4)
    if not hasattr(data, "y") or data.y is None:
        data.y = torch.ones(data.num_edges)
    data.x = torch.tensor(np.array([G.nodes[i]["x"] for i in range(n_zones)]),
                           dtype=torch.float)
    return data

def generate_dataset(n: int = 10000, use_type: str = "residential") -> list:
    dataset  = []
    n_valid  = int(n * 0.7)
    for _ in range(n_valid):
        dataset.append(generate_graph(valid=True,  use_type=use_type))
    for _ in range(n - n_valid):
        dataset.append(generate_graph(valid=False, use_type=use_type))
    random.shuffle(dataset)
    return dataset
