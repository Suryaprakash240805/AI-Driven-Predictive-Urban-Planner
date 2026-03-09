import { Activity, Droplets, Mountain, Users, AlertTriangle } from "lucide-react";

export default function LandInfoPanel({ info }) {
    const items = [
        { label: "Area", value: `${info.area_sqm?.toFixed(0)} m²`, icon: <Activity size={15} />, color: "var(--color-gold)" },
        { label: "NDVI Score", value: info.ndvi?.toFixed(3), icon: <span>🌿</span>, color: "#5DBB63" },
        { label: "NDBI Score", value: info.ndbi?.toFixed(3), icon: <span>🏗️</span>, color: "var(--color-teal)" },
        { label: "Elevation", value: `${info.elevation_m?.toFixed(0)} m`, icon: <Mountain size={15} />, color: "#A78BCA" },
        { label: "Slope", value: `${info.slope_deg?.toFixed(1)}°`, icon: <span>📐</span>, color: "#FFAA00" },
        {
            label: "Groundwater", value: `${info.groundwater_depth?.toFixed(1)} m depth`,
            icon: <Droplets size={15} />, color: "#00C2CB"
        },
    ];

    return (
        <div className="luxury-card" style={{ padding: "20px" }}>
            <h4 style={{
                fontSize: "0.9rem", fontWeight: 600, marginBottom: "16px",
                display: "flex", alignItems: "center", gap: "8px"
            }}>
                <span style={{ color: "var(--color-gold)" }}>🛰️</span> Satellite Analysis
            </h4>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                {items.map((item, i) => (
                    <div key={i} style={{
                        padding: "12px 14px",
                        background: "rgba(255,255,255,0.03)", borderRadius: "10px",
                        border: "1px solid var(--color-border-dim)"
                    }}>
                        <div style={{
                            display: "flex", alignItems: "center", gap: "6px",
                            color: item.color, marginBottom: "4px", fontSize: "0.75rem"
                        }}>
                            {item.icon} {item.label}
                        </div>
                        <p style={{
                            fontWeight: 600, fontSize: "0.95rem", fontFamily: "JetBrains Mono",
                            color: "var(--color-text)"
                        }}>
                            {item.value ?? "—"}
                        </p>
                    </div>
                ))}
            </div>

            {info.flood_risk === 1 && (
                <div className="alert alert-warning" style={{ marginTop: "12px" }}>
                    <AlertTriangle size={15} />
                    <span>Flood-prone zone detected. Extra precautions required.</span>
                </div>
            )}

            {info.is_heritage === 1 && (
                <div className="alert alert-error" style={{ marginTop: "8px" }}>
                    <AlertTriangle size={15} />
                    <span>Heritage protection zone. Construction restrictions apply.</span>
                </div>
            )}
        </div>
    );
}
