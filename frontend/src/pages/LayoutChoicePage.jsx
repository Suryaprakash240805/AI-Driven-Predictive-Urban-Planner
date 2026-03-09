import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle, Loader, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import useProjectStore from "@/store/projectStore";
import useWebSocket from "@/hooks/useWebSocket";
import { generateLayouts, selectLayout } from "@/api/projectApi";

const STRATEGY_META = {
    maximize_builtup: { icon: "🏗️", desc: "Maximizes built-up area (highest FAR ratio)", color: "#D4AF37" },
    maximize_green: { icon: "🌿", desc: "Maximizes green & open spaces (SDG 11 optimal)", color: "#5DBB63" },
    balanced: { icon: "⚖️", desc: "Balanced trade-off: FAR + green + accessibility", color: "#00C2CB" },
};

function LayoutCard({ option, selected, onSelect }) {
    const meta = STRATEGY_META[option.strategy] || {};
    return (
        <div className={`layout-option-card ${selected ? "selected" : ""}`}
            onClick={() => onSelect(option)}
            style={{ borderColor: selected ? meta.color : undefined }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                <div>
                    <span style={{ fontSize: "1.8rem" }}>{meta.icon}</span>
                    <h4 style={{ marginTop: "8px", fontSize: "1rem" }}>Option {option.option_id}</h4>
                    <p style={{ fontSize: "0.75rem", color: "var(--color-muted)", marginTop: "4px" }}>
                        {meta.desc}
                    </p>
                </div>
                <span className="badge" style={{
                    background: `${meta.color}18`, color: meta.color,
                    border: `1px solid ${meta.color}40`, fontSize: "0.65rem"
                }}>
                    Score: {(option.combined_score * 100).toFixed(1)}%
                </span>
            </div>
            <hr className="divider-gold" style={{ margin: "16px 0" }} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                {[
                    ["Feasibility", `${(option.feasibility * 100).toFixed(1)}%`, "#5DBB63"],
                    ["NBC Compliance", `${(option.nbc_compliance * 100).toFixed(1)}%`, "#D4AF37"],
                ].map(([label, val, color]) => (
                    <div key={label}>
                        <p style={{
                            fontSize: "0.7rem", color: "var(--color-muted)",
                            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "4px"
                        }}>{label}</p>
                        <p style={{ fontWeight: 700, color, fontFamily: "JetBrains Mono" }}>{val}</p>
                    </div>
                ))}
            </div>
            {/* Score bar */}
            <div className="progress-bar" style={{ marginTop: "14px" }}>
                <div className="progress-fill" style={{
                    width: `${option.combined_score * 100}%`,
                    background: `linear-gradient(90deg, ${meta.color}, ${meta.color}88)`,
                }} />
            </div>
        </div>
    );
}

export default function LayoutChoicePage() {
    const { currentProject, validationStatus, setSelectedLayout, setValidation } = useProjectStore();
    const [layouts, setLayouts] = useState([]);
    const [selected, setSelected] = useState(null);
    const [status, setStatus] = useState("waiting_v1"); // waiting_v1 | generating | done | rejected
    const nav = useNavigate();

    // WebSocket for real-time HITL updates
    const onWsMessage = useCallback((msg) => {
        if (msg.type === "validation_update") {
            if (msg.stage === 1 && msg.decision === "approved") {
                setStatus("generating");
                setValidation("stage1", "approved");
                toast.success("✅ Validator 1 approved! Generating AI layouts...");
                fetchLayouts();
            }
            if (msg.stage === 1 && msg.decision === "rejected") {
                setStatus("rejected");
                setValidation("stage1", "rejected");
                toast.error("❌ Validator 1 rejected. See feedback.");
            }
            if (msg.type === "layouts_ready") {
                setLayouts(msg.layouts);
                setStatus("done");
            }
        }
    }, []);

    useWebSocket(currentProject?.id, onWsMessage);

    const fetchLayouts = async () => {
        try {
            const res = await generateLayouts(currentProject?.id);
            setLayouts(res.data.options);
            setStatus("done");
        } catch { toast.error("Layout generation failed."); }
    };

    const confirmSelection = async () => {
        if (!selected) return toast.error("Please select one of the layout options");
        try {
            await selectLayout(currentProject?.id, selected.option_id);
            setSelectedLayout(selected);
            toast.success("Layout selected! Proceeding to Validator 2 review.");
            nav(`/report/${currentProject?.id}`);
        } catch { toast.error("Failed to save selection."); }
    };

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title="AI Layout Options" />
                <div className="page-content">

                    <div className="page-header">
                        <div>
                            <h2 className="page-title">AI-Generated Layouts</h2>
                            <p className="page-subtitle">Three optimized land layout options generated by our GNN model</p>
                        </div>
                    </div>

                    {/* HITL Stage tracker */}
                    <div className="luxury-card" style={{ padding: "20px 24px", marginBottom: "24px" }}>
                        <p style={{
                            fontSize: "0.75rem", color: "var(--color-muted)",
                            textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "14px"
                        }}>
                            Validation Pipeline
                        </p>
                        {[
                            { label: "Validator 1 – Land Input Review", stage: "stage1" },
                            { label: "AI Layout Generation", stage: "ai" },
                            { label: "Validator 2 – Construction Feasibility", stage: "stage2" },
                            { label: "Validator 3 – Final Expert Sign-off", stage: "stage3" },
                        ].map((s, i) => {
                            const isActive = (i === 0 && status === "waiting_v1") || (i === 1 && status === "generating");
                            const isDone = validationStatus[s.stage] === "approved" || (i === 1 && status === "done");
                            const isRej = validationStatus[s.stage] === "rejected";
                            return (
                                <div key={i} className={`hitl-stage ${isActive ? "active" : ""} ${isDone ? "approved" : ""} ${isRej ? "rejected" : ""}`}>
                                    <div style={{
                                        width: 28, height: 28, borderRadius: "50%",
                                        background: isDone ? "rgba(93,187,99,0.2)" : isActive ? "rgba(212,175,55,0.2)" : isRej ? "rgba(224,92,92,0.2)" : "rgba(255,255,255,0.04)",
                                        border: `1px solid ${isDone ? "rgba(93,187,99,0.5)" : isActive ? "rgba(212,175,55,0.5)" : isRej ? "rgba(224,92,92,0.5)" : "rgba(255,255,255,0.08)"}`,
                                        display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", flexShrink: 0
                                    }}>
                                        {isDone ? "✓" : isRej ? "✗" : i + 1}
                                    </div>
                                    <span style={{
                                        fontSize: "0.85rem",
                                        color: isDone ? "#5DBB63" : isActive ? "var(--color-gold)" : isRej ? "#E05C5C" : "var(--color-muted)"
                                    }}>
                                        {s.label}
                                    </span>
                                    {isActive && (
                                        <span className="badge badge-pending" style={{ marginLeft: "auto", fontSize: "0.65rem" }}>
                                            In Progress
                                        </span>
                                    )}
                                    {isDone && (
                                        <span className="badge badge-green" style={{ marginLeft: "auto", fontSize: "0.65rem" }}>
                                            Approved
                                        </span>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    {/* Status handling */}
                    {status === "waiting_v1" && (
                        <div className="luxury-card" style={{ padding: "48px", textAlign: "center" }}>
                            <div style={{ fontSize: "3rem", marginBottom: "16px", animation: "pulse 2s infinite" }}>⏳</div>
                            <h3>Awaiting Validator 1 Review</h3>
                            <p style={{ color: "var(--color-muted)", marginTop: "8px", maxWidth: 400, margin: "8px auto 0" }}>
                                Your land input is being reviewed by a registered land verifier.
                                You'll be notified automatically when approved.
                            </p>
                        </div>
                    )}

                    {status === "generating" && (
                        <div className="luxury-card" style={{ padding: "48px", textAlign: "center" }}>
                            <Loader size={40} style={{ color: "var(--color-gold)", animation: "spin 1s linear infinite", margin: "0 auto 16px" }} />
                            <h3>Generating Layout Options</h3>
                            <p style={{ color: "var(--color-muted)", marginTop: "8px" }}>
                                Our GNN model is analyzing your land and generating 3 optimized plans...
                            </p>
                        </div>
                    )}

                    {status === "rejected" && (
                        <div className="alert alert-error" style={{ padding: "24px", borderRadius: 12 }}>
                            <AlertCircle size={20} />
                            <div>
                                <strong>Validator 1 Rejected Your Input</strong>
                                <p style={{ marginTop: "4px", fontSize: "0.85rem" }}>
                                    Please review the feedback and resubmit your land selection.
                                </p>
                            </div>
                        </div>
                    )}

                    {status === "done" && layouts.length > 0 && (
                        <>
                            <div className="grid-3" style={{ marginBottom: "28px" }}>
                                {layouts.map(opt => (
                                    <LayoutCard key={opt.option_id} option={opt}
                                        selected={selected?.option_id === opt.option_id}
                                        onSelect={setSelected} />
                                ))}
                            </div>
                            {selected && (
                                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                                    <button className="btn-primary" onClick={confirmSelection} style={{ gap: "8px" }}>
                                        <CheckCircle size={16} /> Confirm Layout Selection
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
