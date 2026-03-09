import torch
import random
from torch_geometric.data import Data

def add_noise(data: Data, noise_std: float = 0.02) -> Data:
    """Add small Gaussian noise to continuous node features (indices 8-17)."""
    noisy = data.x.clone()
    noisy[:, 8:] += torch.randn_like(noisy[:, 8:]) * noise_std
    noisy[:, 8:] = noisy[:, 8:].clamp(0, 1)
    return Data(x=noisy, edge_index=data.edge_index,
                edge_attr=data.edge_attr, y=data.y)

def drop_edges(data: Data, drop_rate: float = 0.1) -> Data:
    """Randomly drop edges for augmentation."""
    mask = torch.rand(data.num_edges) > drop_rate
    return Data(x=data.x,
                edge_index=data.edge_index[:, mask],
                edge_attr=data.edge_attr[mask] if data.edge_attr is not None else None,
                y=data.y[mask] if data.y is not None and data.y.shape[0] == data.num_edges else data.y)

def augment_dataset(dataset: list, factor: int = 2) -> list:
    augmented = list(dataset)
    for d in dataset:
        for _ in range(factor - 1):
            aug = add_noise(d) if random.random() > 0.5 else drop_edges(d)
            augmented.append(aug)
    random.shuffle(augmented)
    return augmented
