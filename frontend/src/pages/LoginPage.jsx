import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogIn, ShieldCheck, Map, Building2 } from "lucide-react";
import toast from "react-hot-toast";
import useAuthStore from "@/store/authStore";
import { login as loginApi } from "@/api/authApi";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const nav = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // For demo/dev purposes, allow simple login if API fails
      const res = await loginApi({ username, password });
      setAuth(res.data.user, res.data.access_token);
      toast.success(`Welcome back, ${res.data.user.name}!`);
      nav(res.data.user.role.startsWith("validator") ? "/validator" : "/dashboard");
    } catch (err) {
      toast.error("Invalid credentials. Try demo accounts.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg- luxury-black">
      <div className="w-full max-w-md luxury-card overflow-hidden">
        <div className="p-8 pb-4 text-center">
          <div className="w-16 h-16 bg-gold-dim rounded-2xl flex items-center justify-center mx-auto mb-6 border border-gold/20">
            <Building2 className="text-gold" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-gradient-gold mb-2">Urban Planner AI</h1>
          <p className="text-luxury-muted text-sm">Tier-2 & Tier-3 City Development Platform</p>
        </div>

        <form onSubmit={handleLogin} className="p-8 pt-4 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-luxury-muted uppercase tracking-wider">Username</label>
            <input
              type="text"
              className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-gold/50 transition-colors"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-luxury-muted uppercase tracking-wider">Password</label>
            <input
              type="password"
              className="w-full bg-white/5 border border-white/10 rounded-lg p-3 outline-none focus:border-gold/50 transition-colors"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 font-bold flex items-center justify-center gap-2"
          >
            {loading ? <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <LogIn size={18} />}
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <div className="mt-8 pt-6 border-t border-white/5">
            <div className="flex items-center gap-3 text-luxury-muted text-xs">
              <ShieldCheck size={14} className="text-teal-500" />
              <span>NBC 2016 Standards Compliant</span>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
