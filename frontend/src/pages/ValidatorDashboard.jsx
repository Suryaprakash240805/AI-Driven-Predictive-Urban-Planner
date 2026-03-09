import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Eye, Clock } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import useAuthStore from "@/store/authStore";
import { getPendingProjects, approveProject, rejectProject, getValidatorStats } from "@/api/validatorApi";

export default function ValidatorDashboard() {
    const { user, role } = useAuthStore();
    const [queue, setQueue] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [active, setActive] = useState(null);
    const [feedback, setFeedback] = useState("");

    const stageNum = role === "validator_1" ? 1 : role === "validator_2" ? 2 : 3;

    useEffect(() => {
        Promise.all([getPendingProjects(), getValidatorStats()])
            .then(([q, s]) => { setQueue(q.data); setStats(s.data); })
            .finally(() => setLoading(false));
    }, []);

    const handle = async (id, action) => {
        if (action === "reject" && !feedback.trim())
            return toast.error("Please provide feedback before rejecting");
        try {
            if (action === "approve") await approveProject(id, { stage: stageNum });
            else await rejectProject(id, { stage: stageNum, feedback });
            toast.success(action === "approve" ? "✅ Project approved!" : "❌ Project rejected with feedback");
            setQueue(q => q.filter(p => p.id !== id));
            setActive(null); setFeedback("");
        } catch { toast.error("Action failed. Try again."); }
    };

    const STAGE_LABELS = {
        validator_1: "Land & Input Verification",
        validator_2: "Construction Feasibility Review",
        validator_3: "Final Expert Sign-off",
    };

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title={`${STAGE_LABELS[role]} – Stage ${stageNum}`} />
                <div className="page-content">

                    <div className="page-header">
                        <div>
                            <h2 className="page-title">Validator Dashboard</h2>
                            <p className="page-subtitle">{STAGE_LABELS[role]}</p>
                        </div>
                        <span className={`badge ${role === "validator_1" ? "badge-gold" : role === "validator_2" ? "badge-teal" : "badge-purple"}`}
                            style={{ fontSize: "0.8rem", padding: "8px 16px" }}>
                            {user?.name} · Stage {stageNum}
                        </span>
                    </div>

                    {/* Stats */}
                    <div className="grid-stats" style={{ marginBottom: "24px" }}>
                        {[
                            { label: "Pending Review", value: queue.length, color: "gold", icon: "⏳" },
                            { label: "Approved Today", value: stats.approved_today || 0, color: "teal", icon: "✅" },
                            { label: "Rejected Today", value: stats.rejected_today || 0, color: "red", icon: "❌" },
                            { label: "Total Reviewed", value: stats.total || 0, color: "purple", icon: "📊" },
                        ].map((s, i) => (
                            <div key={i} className={`stat-card ${s.color}`}>
                                <div style={{ display: "flex", justifyContent: "space-between" }}>
                                    <div>
                                        <p style={{
                                            fontSize: "0.72rem", color: "var(--color-muted)",
                                            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px"
                                        }}>{s.label}</p>
                                        <h2 style={{ fontSize: "2rem", fontFamily: "Inter", fontWeight: 700 }}>{s.value}</h2>
                                    </div>
                                    <span style={{ fontSize: "1.8rem", opacity: 0.6 }}>{s.icon}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="grid-2">
                        {/* Queue */}
                        <div className="luxury-card" style={{ padding: "24px" }}>
                            <h4 style={{ marginBottom: "16px", fontSize: "0.95rem" }}>
                                Pending Queue ({queue.length})
                            </h4>
                            {loading ? <LoadingSpinner /> : queue.length === 0 ? (
                                <div style={{ textAlign: "center", padding: "32px 0" }}>
                                    <CheckCircle size={40} style={{ color: "#5DBB63", margin: "0 auto 12px" }} />
                                    <p style={{ color: "var(--color-muted)" }}>All caught up! No pending reviews.</p>
                                </div>
                            ) : queue.map(p => (
                                <div key={p.id}
                                    style={{
                                        padding: "14px 16px", borderRadius: "10px", marginBottom: "8px", cursor: "pointer",
                                        background: active?.id === p.id ? "rgba(212,175,55,0.07)" : "rgba(255,255,255,0.02)",
                                        border: `1px solid ${active?.id === p.id ? "rgba(212,175,55,0.3)" : "var(--color-border-dim)"}`,
                                        transition: "all 0.2s"
                                    }}
                                    onClick={() => setActive(p)}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                        <div>
                                            <p style={{ fontWeight: 600, fontSize: "0.875rem" }}>{p.name}</p>
                                            <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", marginTop: "2px" }}>
                                                {p.city} · {p.use_type?.replace("_", " ")}
                                            </p>
                                        </div>
                                        <div style={{ display: "flex", gap: "6px" }}>
                                            <span className="badge badge-pending" style={{ fontSize: "0.65rem" }}>
                                                <Clock size={10} /> Pending
                                            </span>
                                            <button className="btn-ghost" style={{ padding: "5px 10px", fontSize: "0.75rem" }}
                                                onClick={(e) => { e.stopPropagation(); setActive(p); }}>
                                                <Eye size={13} /> Review
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Review Panel */}
                        <div className="luxury-card" style={{ padding: "24px" }}>
                            <h4 style={{ marginBottom: "16px", fontSize: "0.95rem" }}>Review Panel</h4>
                            {!active ? (
                                <div style={{ textAlign: "center", padding: "40px 0" }}>
                                    <p style={{ color: "var(--color-muted)" }}>Select a project from the queue to review</p>
                                </div>
                            ) : (
                                <>
                                    <div style={{ marginBottom: "20px" }}>
                                        <h4 style={{ fontSize: "1rem", marginBottom: "4px" }}>{active.name}</h4>
                                        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                                            <span className="badge badge-teal">{active.city}</span>
                                            <span className="badge badge-purple" style={{ textTransform: "capitalize" }}>
                                                {active.use_type?.replace("_", " ")}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Land info summary */}
                                    <div style={{
                                        padding: "14px", background: "rgba(255,255,255,0.02)",
                                        borderRadius: "10px", border: "1px solid var(--color-border-dim)", marginBottom: "16px"
                                    }}>
                                        {[
                                            ["Area", `${active.land_info?.area_sqm?.toFixed(0)} m²`],
                                            ["NDVI", active.land_info?.ndvi?.toFixed(3)],
                                            ["Flood Risk", active.land_info?.flood_risk ? "⚠️ Yes" : "✅ No"],
                                            ["Heritage", active.land_info?.is_heritage ? "⚠️ Yes" : "✅ No"],
                                        ].map(([k, v]) => (
                                            <div key={k} style={{
                                                display: "flex", justifyContent: "space-between",
                                                padding: "6px 0", borderBottom: "1px solid var(--color-border-dim)",
                                                fontSize: "0.825rem"
                                            }}>
                                                <span style={{ color: "var(--color-muted)" }}>{k}</span>
                                                <span style={{ fontWeight: 500, fontFamily: "JetBrains Mono" }}>{v || "—"}</span>
                                            </div>
                                        ))}
                                    </div>

                                    {/* Feedback */}
                                    <label className="label-luxury">Feedback / Comments</label>
                                    <textarea className="input-luxury" rows={4} style={{ resize: "vertical" }}
                                        placeholder="Provide detailed feedback for approval or rejection..."
                                        value={feedback} onChange={e => setFeedback(e.target.value)} />

                                    <div style={{ display: "flex", gap: "12px", marginTop: "16px" }}>
                                        <button className="btn-primary" style={{ flex: 1, gap: "6px" }}
                                            onClick={() => handle(active.id, "approve")}>
                                            <CheckCircle size={15} /> Approve
                                        </button>
                                        <button className="btn-danger" style={{ flex: 1, gap: "6px" }}
                                            onClick={() => handle(active.id, "reject")}>
                                            <XCircle size={15} /> Reject
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
