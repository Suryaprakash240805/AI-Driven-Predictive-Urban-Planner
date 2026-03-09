import torch
import numpy as np
import geopandas as gpd
from torch_geometric.data import Data
from sklearn.preprocessing import LabelEncoder

ZONE_TYPES = {
    "residential": 0, "commercial": 1, "green_space": 2,
    "road": 3, "parking": 4, "utility": 5, "setback": 6, "industrial": 7,
}

NBC_INCOMPATIBLE = {
    ("residential","industrial"), ("green_space","industrial"),
    ("residential","utility"),    ("commercial","industrial"),
}

def check_nbc_compatibility(a: str, b: str) -> int:
    return 0 if ({a, b} in [set(p) for p in NBC_INCOMPATIBLE]) else 1

def build_graph(gdf: gpd.GeoDataFrame) -> Data:
    n = len(gdf)
    node_feats, edge_src, edge_dst, edge_attrs, labels = [], [], [], [], []
    gdf_proj = gdf.to_crs(epsg=32643)

    for i, row in gdf.iterrows():
        ztype = row.get("zone_type","residential")
        one_hot = np.zeros(8)
        one_hot[ZONE_TYPES.get(ztype, 0)] = 1.0
        feat = np.concatenate([one_hot, [
            float(row.get("area_sqm", 0)) / 10000.0,
            float(row.get("ndvi", 0.0)),
            float(row.get("ndbi", 0.0)),
            float(row.get("pop_density", 0)) / 1000.0,
            float(row.get("elevation_m", 0)) / 100.0,
            float(row.get("slope_deg", 0)) / 45.0,
            float(row.get("flood_risk", 0)),
            float(row.get("groundwater_depth", 5)) / 50.0,
            float(row.get("is_heritage", 0)),
        ]])
        node_feats.append(feat)

    for i in range(n):
        for j in range(i + 1, n):
            gi = gdf_proj.geometry.iloc[i]
            gj = gdf_proj.geometry.iloc[j]
            if gi.touches(gj) or gi.distance(gj) < 1.0:
                slen = gi.intersection(gj).length
                dist = gi.centroid.distance(gj.centroid)
                ef   = [slen / 100.0, dist / 1000.0, 0.0, 1.0]
                lbl  = check_nbc_compatibility(
                    gdf["zone_type"].iloc[i], gdf["zone_type"].iloc[j])
                edge_src += [i, j]; edge_dst += [j, i]
                edge_attrs += [ef, ef]; labels += [lbl, lbl]

    return Data(
        x          = torch.tensor(np.array(node_feats), dtype=torch.float),
        edge_index = torch.tensor([edge_src, edge_dst], dtype=torch.long),
        edge_attr  = torch.tensor(np.array(edge_attrs), dtype=torch.float),
        y          = torch.tensor(labels, dtype=torch.float),
    )
