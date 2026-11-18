import { Calendar } from "lucide-react";

export const AccaddeOggi = ({ pill }) => {
  if (!pill) return null;
  return (
    <div
      data-testid="history-pill-accadde-oggi"
      className="card p-4"
      style={{ background: "linear-gradient(135deg, color-mix(in srgb, var(--accent-amber) 12%, transparent), var(--bg-card))" }}
    >
      <div className="flex items-center gap-2 mb-2">
        <Calendar className="w-4 h-4" style={{ color: "var(--accent-amber)" }} />
        <span className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--accent-amber)" }}>
          {pill.exact === false ? "Accadde in questi giorni" : "Accadde oggi nei mercati"}
        </span>
      </div>
      <div className="font-mono text-[11px] mb-1" style={{ color: "var(--text-muted)" }}>{pill.date}</div>
      <h4 className="font-display text-sm font-bold mb-1" style={{ color: "var(--text-primary)" }}>{pill.title}</h4>
      <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{pill.body}</p>
    </div>
  );
};
