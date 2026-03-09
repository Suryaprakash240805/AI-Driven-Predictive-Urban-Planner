import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Download, FileText, CheckCircle, Loader } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import { getReport, downloadReport, downloadLayout } from "@/api/reportApi";
import { VALIDATION_STAGES } from "@/utils/constants";

export default function FinalReportPage() {
    const { id } = useParams();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getReport(id).then(r => setReport(r.data)).finally(() => setLoading(false));
    }, [id]);

    const downloadFile = async (fn, filename) => {
        try {
            const res = await fn(id);
            const url = URL.createObjectURL(res.data);
            const a = document.createElement("a"); a.href = url; a.download = filename; a.click();
            URL.revokeObjectURL(url);
        } catch { toast.error("Download failed."); }
    };

    if (loading) return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                <LoadingSpinner text="Loading report..." />
            </div>
        </div>
    );

    const isComplete = report?.status === "approved_final";

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title="Project Report" />
                <div className="page-content">

                    <div className="page-header">
                        <div>
                            <h2 className="page-title">{report?.name || "Project Report"}</h2>
                            <p className="page-subtitle">{report?.city} · {report?.use_type?.replace("_", " ")}</p>
                        </div>
                        <div style={{ display: "flex", gap: "10px" }}>
                            <button className="btn-secondary" style={{ gap: "8px" }}
                                onClick={() => downloadFile(downloadLayout, `layout_${id}.png`)}>
                                <Download size={15} /> Download Layout
                            </button>
                            {isComplete && (
                                <button className="btn-primary" style={{ gap: "8px" }}
                                    onClick={() => downloadFile(downloadReport, `report_${id}.pdf`)}>
                                    <FileText size={15} /> Download Full Report
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Validation timeline */}
                    <div className="luxury-card" style={{ padding: "24px", marginBottom: "24px" }}>
                        <h4 style={{ marginBottom: "20px", fontSize: "0.95rem" }}>Validation Timeline</h4>
                        {VALIDATION_STAGES.map((s, i) => {
                            const vd = report?.validations?.find(v => v.stage === s.id);
                            const approved = vd?.decision === "approved";
                            const rejected = vd?.decision === "rejected";
                            return (
                                <div key={s.id} style={{ display: "flex", gap: "16px", marginBottom: "20px" }}>
                                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                                        <div style={{
                                            width: 40, height: 40, borderRadius: "50%",
                                            background: approved ? "rgba(93,187,99,0.15)" : rejected ? "rgba(224,92,92,0.15)" : "rgba(255,255,255,0.04)",
                                            border: `2px solid ${approved ? "rgba(93,187,99,0.5)" : rejected ? "rgba(224,92,92,0.5)" : "rgba(255,255,255,0.1)"}`,
                                            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.1rem"
                                        }}>
                                            {s.icon}
                                        </div>
                                        {i < VALIDATION_STAGES.length - 1 && (
                                            <div style={{
                                                width: 2, flex: 1, minHeight: 28,
                                                background: approved ? "linear-gradient(180deg,#5DBB63,rgba(93,187,99,0.3))" : "rgba(255,255,255,0.06)",
                                                margin: "4px 0"
                                            }} />
                                        )}
                                    </div>
                                    <div style={{ flex: 1, paddingBottom: i < VALIDATION_STAGES.length - 1 ? 20 : 0 }}>
                                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                            <div>
                                                <p style={{ fontWeight: 600, fontSize: "0.9rem" }}>{s.label}</p>
                                                <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", textTransform: "capitalize" }}>
                                                    {s.role.replace("_", " ")}
                                                    {vd?.validator_name ? ` · ${vd.validator_name}` : ""}
                                                </p>
                                            </div>
                                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                                {vd && (
                                                    <span className={`badge ${approved ? "badge-green" : "badge-red"}`}>
                                                        {approved ? "✓ Approved" : "✗ Rejected"}
                                                    </span>
                                                )}
                                                {!vd && (
                                                    <span className="badge badge-pending">⏳ Pending</span>
                                                )}
                                            </div>
                                        </div>
                                        {vd?.feedback && (
                                            <div style={{
                                                marginTop: "8px", padding: "10px 14px",
                                                background: "rgba(255,255,255,0.02)", borderRadius: "8px",
                                                border: "1px solid var(--color-border-dim)",
                                                fontSize: "0.8rem", color: "var(--color-muted)", fontStyle: "italic"
                                            }}>
                                                "{vd.feedback}"
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Report details */}
                    <div className="grid-2">
                        <div className="luxury-card" style={{ padding: "24px" }}>
                            <h4 style={{ marginBottom: "16px", fontSize: "0.95rem" }}>Land Details</h4>
                            {[
                                ["Location", report?.city],
                                ["Coordinates", report?.land_info?.centroid || "—"],
                                ["Area", `${report?.land_info?.area_sqm?.toFixed(0)} m²`],
                                ["NDVI Score", report?.land_info?.ndvi?.toFixed(3)],
                                ["Elevation", `${report?.land_info?.elevation_m?.toFixed(0)} m`],
                                ["Flood Risk", report?.land_info?.flood_risk ? "Yes ⚠️" : "No ✅"],
                            ].map(([k, v]) => (
                                <div key={k} style={{
                                    display: "flex", justifyContent: "space-between",
                                    padding: "10px 0", borderBottom: "1px solid var(--color-border-dim)", fontSize: "0.85rem"
                                }}>
                                    <span style={{ color: "var(--color-muted)" }}>{k}</span>
                                    <span style={{ fontWeight: 500, fontFamily: "JetBrains Mono", fontSize: "0.8rem" }}>{v}</span>
                                </div>
                            ))}
                        </div>

                        <div className="luxury-card" style={{ padding: "24px" }}>
                            <h4 style={{ marginBottom: "16px", fontSize: "0.95rem" }}>Selected Layout</h4>
                            {report?.selected_layout ? (
                                <>
                                    <div style={{
                                        background: "rgba(255,255,255,0.02)", borderRadius: "10px", padding: "16px",
                                        border: "1px solid var(--color-border-dim)", marginBottom: "14px"
                                    }}>
                                        <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", marginBottom: "4px" }}>Strategy</p>
                                        <p style={{ fontWeight: 600, textTransform: "capitalize" }}>
                                            {report.selected_layout.strategy?.replace("_", " ")}
                                        </p>
                                    </div>
                                    {[
                                        ["Feasibility", `${(report.selected_layout.feasibility * 100).toFixed(1)}%`, "#5DBB63"],
                                        ["NBC Compliance", `${(report.selected_layout.nbc_compliance * 100).toFixed(1)}%`, "#D4AF37"],
                                        ["Combined Score", `${(report.selected_layout.combined_score * 100).toFixed(1)}%`, "#00C2CB"],
                                    ].map(([k, v, c]) => (
                                        <div key={k} style={{
                                            display: "flex", justifyContent: "space-between",
                                            padding: "10px 0", borderBottom: "1px solid var(--color-border-dim)", fontSize: "0.85rem"
                                        }}>
                                            <span style={{ color: "var(--color-muted)" }}>{k}</span>
                                            <span style={{ fontWeight: 700, fontFamily: "JetBrains Mono", color: c }}>{v}</span>
                                        </div>
                                    ))}
                                </>
                            ) : (
                                <p style={{ color: "var(--color-muted)", textAlign: "center", padding: "24px 0" }}>
                                    Layout selection pending...
                                </p>
                            )}
                        </div>
                    </div>

                    {isComplete && (
                        <div className="alert alert-success" style={{ marginTop: "20px", padding: "20px 24px" }}>
                            <CheckCircle size={20} />
                            <div>
                                <strong>Project Fully Approved!</strong>
                                <p style={{ marginTop: "4px", fontSize: "0.85rem" }}>
                                    All 3 validators have approved your project.
                                    Download your complete report with all validator signatures.
                                </p>
                            </div>
                            <button className="btn-primary" style={{ marginLeft: "auto", flexShrink: 0, gap: "8px" }}
                                onClick={() => downloadFile(downloadReport, `urban_plan_report_${id}.pdf`)}>
                                <Download size={14} /> Download PDF
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
