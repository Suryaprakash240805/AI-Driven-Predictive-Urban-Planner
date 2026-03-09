import { Bell, User } from "lucide-react";
import useAuthStore from "@/store/authStore";

export default function Navbar({ title = "Overview" }) {
  const { user } = useAuthStore();

  return (
    <header className="h-16 border-b border-white/10 flex items-center justify-between px-8 bg-luxury-black/80 backdrop-blur-md sticky top-0 z-50">
      <h1 className="text-lg font-semibold">{title}</h1>

      <div className="flex items-center gap-6">
        <button className="text-luxury-muted hover:text-white transition-colors relative">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-gold rounded-full" />
        </button>

        <div className="flex items-center gap-3 pl-6 border-l border-white/10">
          <div className="text-right">
            <p className="text-sm font-medium">{user?.name || 'Guest API User'}</p>
            <p className="text-[10px] text-luxury-muted uppercase tracking-wider">{user?.role?.replace('_', ' ') || 'No Role'}</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden">
            <User size={20} className="text-luxury-muted" />
          </div>
        </div>
      </div>
    </header>
  );
}
