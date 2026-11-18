import { X } from "lucide-react";
import { useEffect } from "react";

export const Modal = ({ open, onClose, title, subtitle, children, size = "md" }) => {
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [open]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center" onClick={onClose} data-testid="generic-modal">
      <div className="absolute inset-0" style={{ background: "rgba(0,0,0,0.65)" }} />
      <div
        onClick={(e) => e.stopPropagation()}
        className={`relative w-full ${size === "lg" ? "sm:max-w-2xl" : "sm:max-w-md"} max-h-[88dvh] overflow-y-auto rounded-t-3xl sm:rounded-3xl`}
        style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between px-4 py-3" style={{ background: "var(--bg-surface)", borderBottom: "1px solid var(--border)" }}>
          <div className="min-w-0 pr-3">
            {subtitle && (
              <div className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--accent-amber)" }}>
                {subtitle}
              </div>
            )}
            <div className="font-display text-sm font-bold truncate" style={{ color: "var(--text-primary)" }}>{title}</div>
          </div>
          <button onClick={onClose} className="btn-ghost !p-2" aria-label="Chiudi"><X className="w-4 h-4" /></button>
        </div>
        <div className="px-5 py-4">{children}</div>
      </div>
    </div>
  );
};
