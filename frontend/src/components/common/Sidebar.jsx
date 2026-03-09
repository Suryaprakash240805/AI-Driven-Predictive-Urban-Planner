import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Users, FileText, Settings, LogOut, Building, Map } from "lucide-react";
import useAuthStore from "@/store/authStore";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, role: "user" },
  { to: "/build-type", label: "New Project", icon: Building, role: "user" },
  { to: "/validator", label: "Review Queue", icon: FileText, role: "validator" },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const nav = useNavigate();

  const handleLogout = () => {
    logout();
    nav("/login");
  };

  const filteredLinks = LINKS.filter(link =>
    link.role === "user" ? user?.role === "user" : user?.role?.startsWith("validator")
  );

  return (
    <div className="w-64 h-screen border-r border-white/10 flex flex-col p-4 bg-luxury-dark sticky top-0">
      <div className="flex items-center gap-3 px-2 mb-10">
        <div className="w-8 h-8 bg-gold rounded-lg flex items-center justify-center">
          <Map size={18} className="text-black" />
        </div>
        <span className="font-bold text-lg text-gradient-gold">UrbanPlan AI</span>
      </div>

      <nav className="flex-1 space-y-1">
        {filteredLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all
              ${isActive ? 'bg-gold/10 text-gold font-medium' : 'text-luxury-muted hover:text-white hover:bg-white/5'}
            `}
          >
            <link.icon size={18} />
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="pt-4 mt-4 border-t border-white/5 space-y-1">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-400/5 transition-all"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </div>
  );
}
