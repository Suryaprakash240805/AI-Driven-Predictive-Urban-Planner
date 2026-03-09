import torch
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle, os

class NodeFeatureNormalizer:
    def __init__(self):
        self.scaler = StandardScaler()

    def fit(self, dataset: list):
        all_x = torch.cat([d.x for d in dataset], dim=0).numpy()
        self.scaler.fit(all_x)

    def transform(self, dataset: list) -> list:
        for d in dataset:
            d.x = torch.tensor(
                self.scaler.transform(d.x.numpy()), dtype=torch.float)
        return dataset

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self.scaler, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            self.scaler = pickle.load(f)
