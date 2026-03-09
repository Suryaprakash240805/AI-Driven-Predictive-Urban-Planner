import torch
import geopandas as gpd
from shapely.geometry import box, Polygon
from ml.src.data_pipeline.graph_builder import build_graph
from ml.src.inference.plot_exporter import export_layout_plot

STRATEGIES = ["maximize_builtup", "maximize_green", "balanced"]

def _make_gdf(land: Polygon, strategy: str) -> gpd.GeoDataFrame:
    b = land.bounds
    minx, miny, maxx, maxy = b
    W, H = maxx - minx, maxy - miny
    if strategy == "maximize_builtup":
        zones = [
            ("road",        box(minx, miny, maxx, miny + H*.10)),
            ("setback",     box(minx, miny+H*.10, minx+W*.05, maxy)),
            ("setback",     box(maxx-W*.05, miny+H*.10, maxx, maxy)),
            ("residential", box(minx+W*.05, miny+H*.10, maxx-W*.05, maxy-H*.10)),
            ("parking",     box(minx+W*.05, maxy-H*.10, maxx-W*.05, maxy)),
        ]
    elif strategy == "maximize_green":
        zones = [
            ("road",        box(minx, miny, maxx, miny+H*.10)),
            ("green_space", box(minx, miny+H*.10, minx+W*.30, maxy)),
            ("residential", box(minx+W*.30, miny+H*.10, maxx-W*.10, maxy)),
            ("setback",     box(maxx-W*.10, miny+H*.10, maxx, maxy)),
        ]
    else:
        zones = [
            ("road",        box(minx, miny, maxx, miny+H*.10)),
            ("setback",     box(minx, miny+H*.10, minx+W*.05, maxy)),
            ("green_space", box(minx+W*.05, miny+H*.10, minx+W*.25, maxy)),
            ("residential", box(minx+W*.25, miny+H*.10, maxx-W*.15, maxy)),
            ("parking",     box(maxx-W*.15, miny+H*.10, maxx-W*.05, maxy)),
            ("setback",     box(maxx-W*.05, miny+H*.10, maxx, maxy)),
        ]
    rows = [{"zone_type": zt, "geometry": g, "area_sqm": g.area,
             "ndvi": .5 if zt=="green_space" else .1} for zt, g in zones]
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")

def generate_options(land_polygon: dict, use_type: str,
                     model, device) -> list[dict]:
    from shapely.geometry import shape
    land = shape(land_polygon.get("geometry", land_polygon))
    options = []

    for i, strat in enumerate(STRATEGIES):
        gdf   = _make_gdf(land, strat)
        graph = build_graph(gdf).to(device)
        model.eval()
        with torch.no_grad():
            g_score, e_scores = model(
                graph.x, graph.edge_index, graph.edge_attr,
                torch.zeros(graph.num_nodes, dtype=torch.long, device=device))

        feasibility    = float(g_score.item())
        nbc_compliance = float(e_scores.mean().item())
        combined       = round(0.6 * feasibility + 0.4 * nbc_compliance, 4)
        img_path       = f"/tmp/layout_option_{i+1}.png"
        export_layout_plot(gdf, strat, i+1, feasibility, nbc_compliance, img_path)

        options.append({
            "option_id":      i + 1,
            "strategy":       strat,
            "feasibility":    round(feasibility, 4),
            "nbc_compliance": round(nbc_compliance, 4),
            "combined_score": combined,
            "geojson":        gdf.__geo_interface__,
            "image_path":     img_path,
        })

    options.sort(key=lambda o: o["combined_score"], reverse=True)
    return options
