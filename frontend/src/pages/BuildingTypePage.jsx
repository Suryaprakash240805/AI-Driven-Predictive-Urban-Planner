import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";
import Sidebar from "@/components/common/Sidebar";
import Navbar from "@/components/common/Navbar";
import useProjectStore from "@/store/projectStore";
import { BUILD_TYPES } from "@/utils/constants";

export default function BuildingTypePage() {
    const { setBuildingType } = useProjectStore();
    const [selected, setSelected] = useState(null);
    const nav = useNavigate();

    const proceed = () => {
        if (!selected) return toast.error("Please select a building type");
        setBuildingType(selected);
        nav("/land-select");
    };

    return (
        <div style={{ display: "flex" }}>
            <Sidebar />
            <div className="page-wrapper">
                <Navbar title="Project Setup" />
                <div className="page-content">

                    {/* Step indicator */}
                    <div className="step-indicator" style={{ maxWidth: 500, marginBottom: "32px" }}>
                        {[1, 2, 3, 4].map((s, i, arr) => (
                            <div key={s} style={{ display: "flex", alignItems: "center", flex: i < arr.length - 1 ? 1 : "unset" }}>
                                <div className={`step-dot ${s === 1 ? "active" : ""}`}>{s}</div>
                                {i < arr.length - 1 && <div className="step-line" />}
                            </div>
                        ))}
                    </div>
                    <div style={{
                        display: "flex", gap: "12px", marginBottom: "8px", fontSize: "0.78rem",
                        color: "var(--color-muted)", maxWidth: 500, justifyContent: "space-between"
                    }}>
                        <span style={{ color: "var(--color-gold)", fontWeight: 600 }}>Build Type</span>
                        <span>Land Selection</span>
                        <span>AI Layout</span>
                        <span>Final Report</span>
                    </div>

                    <div className="page-header" style={{ marginTop: "24px" }}>
                        <div>
                            <h2 className="page-title">What do you want to build?</h2>
                            <p className="page-subtitle">Select the purpose of your land development</p>
                        </div>
                    </div>

                    {/* Type Cards */}
                    <div className="grid-3" style={{ marginBottom: "32px" }}>
                        {BUILD_TYPES.map(bt => (
                            <div key={bt.id}
                                className="layout-option-card"
                                style={{
                                    padding: "28px 24px",
                                    borderColor: selected?.id === bt.id ? bt.color : undefined
                                }}
                                onClick={() => setSelected(bt)}>
                                {selected?.id === bt.id && (
                                    <CheckCircle size={20} style={{
                                        position: "absolute", top: 16, right: 16,
                                        color: bt.color
                                    }} />
                                )}
                                <div style={{ fontSize: "3rem", marginBottom: "16px" }}>{bt.icon}</div>
                                <h3 style={{ fontSize: "1.1rem", marginBottom: "8px", color: "var(--color-text)" }}>
                                    {bt.label}
                                </h3>
                                <p style={{ fontSize: "0.85rem", color: "var(--color-muted)", lineHeight: 1.6 }}>
                                    {bt.desc}
                                </p>
                                <div style={{ marginTop: "16px" }}>
                                    <span className="badge" style={{
                                        background: `${bt.color}15`, color: bt.color,
                                        border: `1px solid ${bt.color}40`,
                                    }}>
                                        NBC 2016 Compliant
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div style={{ display: "flex", justifyContent: "flex-end" }}>
                        <button className="btn-primary" onClick={proceed} style={{ gap: "10px" }}>
                            Continue to Land Selection <ArrowRight size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
