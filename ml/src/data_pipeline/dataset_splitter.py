import random
from torch_geometric.data import Data

def split_dataset(dataset: list, train=0.70, val=0.15, test=0.15, seed=42):
    random.seed(seed)
    random.shuffle(dataset)
    n = len(dataset)
    t = int(n * train)
    v = int(n * (train + val))
    return dataset[:t], dataset[t:v], dataset[v:]
