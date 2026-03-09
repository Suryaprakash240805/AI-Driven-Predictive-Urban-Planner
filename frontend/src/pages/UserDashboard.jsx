import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FolderOpen, CheckCircle, Clock, Plus, ArrowRight, Activity } from "lucide-react";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import useAuthStore from "@/store/authStore";
import { getMyProjects } from "@/api/projectApi";
import { VALIDATION_STAGES } from "@/utils/constants";

const STATS = (projects) => [
    {
        label: "Total Projects", value: projects.length,
        icon: "📁", color: "gold", sub: "All time"
    },
    {
        label: "Approved", value: projects.filter(p => p.status === "approved").length,
        icon: "✅", color: "teal", sub: "Fully validated"
    },
    {
        label: "In Review", value: projects.filter(p => p.status === "in_review").length,
        icon: "⏳", color: "purple", sub: "Awaiting validator"
    },
    {
        label: "Rejected", value: projects.filter(p => p.status === "rejected").length,
        icon: "❌", color: "red", sub: "Needs revision"
    },
];

function StageBar({ project }) {
    const stages = [1, 2, 3];
    const cur = project.current_stage || 0;
    return (
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "12px" }}>
            {stages.map((s, i) => (
                <div key={s} style={{ display: "flex", alignItems: "center", gap: "8px", flex: 1 }}>
                    <div style={{
                        width: 28, height: 28, borderRadius: "50%",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: "0.7rem", fontWeight: 700, flexShrink: 0,
                        background: cur > s ? "rgba(93,187,99,0.15)"
                            : cur === s ? "rgba(212,175,55,0.15)" : "rgba(255,255,255,0.04)",
                        border: cur > s ? "1px solid rgba(93,187,99,0.4)"
                            : cur === s ? "1px solid rgba(212,175,55,0.4)" : "1px solid rgba(255,255,255,0.06)",
                        color: cur > s ? "#5DBB63" : cur === s ? "var(--color-gold)" : "var(--color-muted)",
                    }}>{cur > s ? "✓" : s}</div>
                    {i < stages.length - 1 && (
                        <div style={{
                            flex: 1, height: 2, borderRadius: 1,
                            background: cur > s ? "linear-gradient(90deg,#5DBB63,#D4AF37)"
                                : "rgba(255,255,255,0.06)"
                        }} />
                    )}
                </div>
            ))}
        </div>
    );
}

export default function UserDashboard() {
    const { user } = useAuthStore();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const nav = useNavigate();

    useEffect(() => {
        getMyProjects()
            .then(r => setProjects(r.data))
            .catch(() => setProjects([]))
            .finally(() => setLoading(false));
    }, []);

    const stats = STATS(projects);

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title="Dashboard" />
                <div className="page-content">

                    {/* Welcome Banner */}
                    <div className="luxury-card" style={{
                        padding: "28px 32px", marginBottom: "24px",
                        background: "linear-gradient(135deg, rgba(18,18,42,0.98), rgba(13,13,43,0.99))"
                    }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <h2 style={{ fontSize: "1.5rem", marginBottom: "8px" }}>
                                    Welcome back, <span className="text-gradient-gold">{user?.name}</span> 👋
                                </h2>
                                <p style={{ color: "var(--color-muted)", fontSize: "0.9rem" }}>
                                    Plan your land with AI assistance and expert validation
                                </p>
                                <div style={{ display: "flex", gap: "10px", marginTop: "14px" }}>
                                    <span className="badge badge-teal">🤖 AI-Powered</span>
                                    <span className="badge badge-gold">🏙️ NBC 2016 Compliant</span>
                                    <span className="badge badge-purple">🔍 3-Stage HITL</span>
                                </div>
                            </div>
                            <button className="btn-primary" onClick={() => nav("/build-type")}
                                style={{ gap: "8px", flexShrink: 0 }}>
                                <Plus size={16} /> New Project
                            </button>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid-stats" style={{ marginBottom: "28px" }}>
                        {stats.map((s, i) => (
                            <div key={i} className={`stat-card ${s.color}`} style={{ padding: "22px 24px" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                    <div>
                                        <p style={{
                                            fontSize: "0.75rem", color: "var(--color-muted)",
                                            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "8px"
                                        }}>
                                            {s.label}
                                        </p>
                                        <h2 style={{
                                            fontSize: "2.2rem", fontFamily: "Inter", fontWeight: 700,
                                            lineHeight: 1, marginBottom: "6px"
                                        }}>{s.value}</h2>
                                        <p style={{ fontSize: "0.75rem", color: "var(--color-muted)" }}>{s.sub}</p>
                                    </div>
                                    <span style={{ fontSize: "2rem", opacity: 0.7 }}>{s.icon}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Projects Table */}
                    <div className="luxury-card" style={{ padding: "24px" }}>
                        <div style={{
                            display: "flex", justifyContent: "space-between",
                            alignItems: "center", marginBottom: "20px"
                        }}>
                            <h3 style={{ fontSize: "1.1rem" }}>My Projects</h3>
                            <button className="btn-ghost" style={{ fontSize: "0.8rem" }}
                                onClick={() => nav("/build-type")}>
                                <Plus size={14} /> New
                            </button>
                        </div>

                        {loading ? <LoadingSpinner text="Loading projects..." /> :
                            projects.length === 0 ? (
                                <div style={{ textAlign: "center", padding: "48px 0" }}>
                                    <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🏗️</div>
                                    <h4 style={{ color: "var(--color-muted)", marginBottom: "8px" }}>No projects yet</h4>
                                    <p style={{ color: "var(--color-muted)", fontSize: "0.875rem", marginBottom: "20px" }}>
                                        Start planning your land with AI assistance
                                    </p>
                                    <button className="btn-primary" onClick={() => nav("/build-type")}>
                                        <Plus size={15} /> Create First Project
                                    </button>
                                </div>
                            ) : (
                                <table className="luxury-table">
                                    <thead>
                                        <tr>
                                            <th>Project</th>
                                            <th>Type</th>
                                            <th>Location</th>
                                            <th>Status</th>
                                            <th>Validation</th>
                                            <th>Created</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {projects.map(p => (
                                            <tr key={p.id}>
                                                <td style={{ fontWeight: 500 }}>{p.name}</td>
                                                <td>
                                                    <span className="badge badge-purple" style={{ textTransform: "capitalize" }}>
                                                        {p.use_type?.replace("_", " ")}
                                                    </span>
                                                </td>
                                                <td style={{ color: "var(--color-muted)", fontSize: "0.8rem" }}>{p.city}</td>
                                                <td>
                                                    <span className={`badge ${p.status === "approved" ? "badge-green" :
                                                            p.status === "rejected" ? "badge-red" :
                                                                p.status === "in_review" ? "badge-pending" : "badge-teal"
                                                        }`} style={{ textTransform: "capitalize" }}>
                                                        {p.status?.replace("_", " ")}
                                                    </span>
                                                </td>
                                                <td style={{ minWidth: 160 }}><StageBar project={p} /></td>
                                                <td style={{ color: "var(--color-muted)", fontSize: "0.8rem" }}>
                                                    {new Date(p.created_at).toLocaleDateString("en-IN")}
                                                </td>
                                                <td>
                                                    <button className="btn-ghost" style={{ padding: "6px 12px", fontSize: "0.8rem" }}
                                                        onClick={() => nav(`/report/${p.id}`)}>
                                                        View <ArrowRight size={13} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                    </div>
                </div>
            </div>
        </div>
    );
}
