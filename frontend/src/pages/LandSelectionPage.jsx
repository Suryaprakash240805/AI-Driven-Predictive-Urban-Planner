import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Loader, MapPin, AlertTriangle } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import MapContainer from "@/components/map/MapContainer";
import LandInfoPanel from "@/components/map/LandInfoPanel";
import useProjectStore from "@/store/projectStore";
import { analyzeLand, createProject } from "@/api/projectApi";

export default function LandSelectionPage() {
    const { buildingType, setLandPolygon, setLandInfo, setProject } = useProjectStore();
    const [polygon, setPolygon] = useState(null);
    const [landInfo, setLandInfoLocal] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const nav = useNavigate();

    const onPolygonDrawn = async (geo) => {
        setPolygon(geo);
        setAnalyzing(true);
        try {
            const res = await analyzeLand(geo);
            setLandInfoLocal(res.data);
            setLandInfo(res.data);
            toast.success("Land analysis complete!");
        } catch {
            toast.error("Failed to analyze land. Please try again.");
        } finally { setAnalyzing(false); }
    };

    const proceed = async () => {
        if (!polygon) return toast.error("Please draw your land boundary on the map");
        try {
            const res = await createProject({
                use_type: buildingType?.id,
                land_polygon: polygon,
                land_info: landInfo,
            });
            setProject(res.data);
            setLandPolygon(polygon);
            toast.success("Project created! Awaiting Validator 1 review.");
            nav("/layout-choice");
        } catch { toast.error("Failed to submit project."); }
    };

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title="Land Selection" />
                <div className="page-content">

                    <div className="page-header">
                        <div>
                            <h2 className="page-title">Select Your Land</h2>
                            <p className="page-subtitle">
                                Draw your land boundary on the satellite map using the polygon tool
                            </p>
                        </div>
                        {polygon && (
                            <button className="btn-primary" onClick={proceed} style={{ gap: "8px" }}>
                                Submit for Review <ArrowRight size={15} />
                            </button>
                        )}
                    </div>

                    {/* Instructions */}
                    <div className="alert alert-info" style={{ marginBottom: "20px" }}>
                        <MapPin size={16} />
                        <span>
                            Use the <strong>polygon tool (◇)</strong> on the map to draw your land boundary.
                            Sentinel-2 satellite imagery will be used for land analysis.
                        </span>
                    </div>

                    <div className="grid-2" style={{ gap: "20px" }}>
                        {/* Map */}
                        <div style={{ height: 520 }}>
                            <div className="map-wrapper" style={{ height: "100%" }}>
                                <MapContainer onPolygonDrawn={onPolygonDrawn} />
                            </div>
                        </div>

                        {/* Info Panel */}
                        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            {analyzing && (
                                <div className="luxury-card" style={{ padding: "28px", textAlign: "center" }}>
                                    <Loader size={32} style={{
                                        color: "var(--color-gold)",
                                        animation: "spin 1s linear infinite", margin: "0 auto 12px"
                                    }} />
                                    <p style={{ color: "var(--color-muted)" }}>
                                        Analyzing land via Sentinel-2 satellite data...
                                    </p>
                                </div>
                            )}

                            {landInfo && !analyzing && <LandInfoPanel info={landInfo} />}

                            {!polygon && !analyzing && (
                                <div className="luxury-card" style={{ padding: "28px", textAlign: "center" }}>
                                    <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🛰️</div>
                                    <h4 style={{ marginBottom: "8px" }}>Draw Your Land</h4>
                                    <p style={{ color: "var(--color-muted)", fontSize: "0.85rem" }}>
                                        Click the polygon tool on the map and click to mark your land corners.
                                        Double-click to complete the boundary.
                                    </p>
                                </div>
                            )}

                            {/* Building type badge */}
                            {buildingType && (
                                <div className="luxury-card" style={{ padding: "16px 20px" }}>
                                    <p style={{
                                        fontSize: "0.75rem", color: "var(--color-muted)",
                                        textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "8px"
                                    }}>
                                        Selected Build Type
                                    </p>
                                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                        <span style={{ fontSize: "2rem" }}>{buildingType.icon}</span>
                                        <div>
                                            <p style={{ fontWeight: 600 }}>{buildingType.label}</p>
                                            <p style={{ color: "var(--color-muted)", fontSize: "0.8rem" }}>
                                                {buildingType.desc}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
