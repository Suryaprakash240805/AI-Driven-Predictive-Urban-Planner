import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd

ZONE_COLORS = {
    "residential": "#FFD700", "commercial": "#4A90D9",
    "green_space": "#5DBB63", "road": "#9E9E9E",
    "parking": "#B0BEC5",     "utility": "#FF8A65",
    "setback": "#555577",     "industrial": "#E05C5C",
}

def export_layout_plot(gdf: gpd.GeoDataFrame, strategy: str,
                        option_id: int, feasibility: float,
                        nbc_compliance: float, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="#0A0A1E")
    ax.set_aspect("equal"); ax.set_facecolor("#0A0A1E")
    ax.tick_params(colors="#7A7A9A"); ax.spines[:].set_color("#2A2A5A")

    for _, row in gdf.iterrows():
        color = ZONE_COLORS.get(row["zone_type"], "#CCCCCC")
        x, y  = row.geometry.exterior.xy
        ax.fill(x, y, color=color, alpha=0.8, edgecolor="#D4AF37", linewidth=1.0)
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        ax.text(cx, cy, f"{row['zone_type']}\n{row.get('area_sqm',0):.0f}m²",
                ha="center", va="center", fontsize=7.5, fontweight="bold",
                color="white", bbox=dict(boxstyle="round,pad=0.2",
                                          facecolor="#0A0A1E", alpha=0.6, edgecolor="none"))

    handles = [mpatches.Patch(color=c, label=z)
               for z, c in ZONE_COLORS.items()
               if z in gdf["zone_type"].values]
    leg = ax.legend(handles=handles, loc="upper right", fontsize=8,
                    facecolor="#181835", edgecolor="#D4AF37", labelcolor="white")

    ax.set_title(
        f"Layout Option {option_id} — {strategy.replace('_',' ').title()}\n"
        f"Feasibility: {feasibility:.1%}  |  NBC Compliance: {nbc_compliance:.1%}",
        color="#D4AF37", fontsize=11, fontweight="bold", pad=14,
    )
    ax.set_xlabel("X (m)", color="#7A7A9A"); ax.set_ylabel("Y (m)", color="#7A7A9A")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="#0A0A1E")
    plt.close()
