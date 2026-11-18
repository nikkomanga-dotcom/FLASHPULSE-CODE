import { useState } from "react";
import { ChevronDown, ChevronUp, Sparkles, ArrowRight, Clock } from "lucide-react";

const impactClass = (s) => s >= 8 ? "impact-high" : s >= 5 ? "impact-med" : "impact-low";

const timeAgo = (iso) => {
  const diff = (Date.now() - new Date(iso).getTime()) / 60000;
  if (!Number.isFinite(diff)) return "";
  if (diff < 1) return "ora";
  if (diff < 60) return `${Math.round(diff)}m fa`;
  if (diff < 1440) return `${Math.round(diff / 60)}h fa`;
  return `${Math.round(diff / 1440)}g fa`;
};

export const FlashCard = ({ item, onOpen, onAsk }) => {
  const [openDomino, setOpenDomino] = useState(false);
  return (
    <article className="card p-4" data-testid={`flash-card-${item.id}`}>
      <div className="flex items-start gap-3 mb-2">
        <span
          className={`chip ${impactClass(item.impact)} shrink-0`}
          data-testid="impact-score-badge"
          title="Impact Score 1-10"
        >
          Impact {item.impact}/10
        </span>
        <div className="flex items-center gap-1 ml-auto text-[11px]" style={{ color: "var(--text-muted)" }}>
          <Clock className="w-3 h-3" />
          {timeAgo(item.published_at)}
        </div>
      </div>

      <h3 className="font-display text-base font-bold leading-snug mb-2" style={{ color: "var(--text-primary)" }}>
        {item.title}
      </h3>

      <ul className="space-y-1.5 mb-3">
        {(item.bullets || []).map((b, i) => (
          <li key={i} className="flex items-start gap-2 text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ background: "var(--accent-amber)" }} />
            {b}
          </li>
        ))}
      </ul>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {(item.tags || []).map((t) => (
          <span key={t} className="chip" style={{ color: "var(--accent-indigo)" }}>{t}</span>
        ))}
        {item.sources?.slice(0, 2).map((s) => (
          <span key={s} className="chip">· {s}</span>
        ))}
      </div>

      {item.domino && (<>
      <button
        onClick={() => setOpenDomino((v) => !v)}
        data-testid="effetto-domino-toggle"
        className="w-full text-left rounded-lg px-3 py-2 text-xs flex items-center justify-between"
        style={{ background: "var(--bg-elevated)", color: "var(--text-secondary)" }}
      >
        <span className="font-mono uppercase tracking-wider text-[10px] font-bold" style={{ color: "var(--accent-amber)" }}>
          Effetto Domino
        </span>
        {openDomino ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>
      {openDomino && (
        <p className="mt-2 text-xs leading-relaxed px-3" style={{ color: "var(--text-secondary)" }}>
          {item.domino}
        </p>
      )}
      </>)}

      <div className="flex items-center gap-2 mt-3">
        <button
          data-testid="news-level2-trigger"
          onClick={() => onOpen(item)}
          className="btn-primary flex-1 justify-center"
        >
          Approfondisci <ArrowRight className="w-4 h-4" />
        </button>
        <button
          data-testid="ask-ai-trigger"
          onClick={() => onAsk(item)}
          className="btn-ghost"
          title="Chiedi all'IA Copilot"
        >
          <Sparkles className="w-4 h-4" />
          Chiedi IA
        </button>
      </div>
    </article>
  );
};
