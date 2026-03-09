import { Loader2 } from "lucide-react";

export default function LoadingSpinner({ text = "Loading dashboard..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 className="text-gold animate-spin" size={40} />
      <p className="text-luxury-muted text-sm">{text}</p>
    </div>
  );
}
