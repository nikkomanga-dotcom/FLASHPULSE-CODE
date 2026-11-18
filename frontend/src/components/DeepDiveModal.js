import { useEffect } from "react";
import { X, Sparkles, BookOpen, TrendingUp, TrendingDown } from "lucide-react";

export const DeepDiveModal = ({ item, onClose, onAsk }) => {
  useEffect(() => {
    if (!item) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = prev; };
  }, [item]);

  if (!item) return null;
  const dd = item.deep_dive || {};

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
      onClick={onClose}
      data-testid="level2-modal"
    >
      <div className="absolute inset-0" style={{ background: "rgba(0,0,0,0.6)" }} />
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full sm:max-w-xl max-h-[92dvh] overflow-y-auto rounded-t-3xl sm:rounded-3xl"
        style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between px-4 py-3" style={{ background: "var(--bg-surface)", borderBottom: "1px solid var(--border)" }}>
          <span className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--accent-amber)" }}>
            Approfondimento · Impact {item.impact}/10
          </span>
          <button onClick={onClose} className="btn-ghost !p-2" aria-label="Chiudi">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="px-5 py-4 space-y-5">
          <h2 className="font-display text-xl font-bold leading-snug" style={{ color: "var(--text-primary)" }}>
            {item.title}
          </h2>

          <div className="flex flex-wrap gap-1.5">
            {(item.tags || []).map((t) => <span key={t} className="chip" style={{ color: "var(--accent-indigo)" }}>{t}</span>)}
            {item.sources?.map((s) => <span key={s} className="chip">· {s}</span>)}
          </div>

          {dd.analysis && (
            <section>
              <h3 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-2" style={{ color: "var(--text-muted)" }}>Analisi</h3>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{dd.analysis}</p>
            </section>
          )}

          {(dd.bull || dd.bear) && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="card p-3">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 price-up" />
                <span className="font-mono text-[10px] uppercase tracking-wider font-bold price-up">Bull Case</span>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{dd.bull}</p>
            </div>
            <div className="card p-3">
              <div className="flex items-center gap-2 mb-1">
                <TrendingDown className="w-4 h-4 price-down" />
                <span className="font-mono text-[10px] uppercase tracking-wider font-bold price-down">Bear Case</span>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{dd.bear}</p>
            </div>
          </div>
          )}

          {dd.history?.body && (
            <section className="card p-4" data-testid="la-storia-insegna-card" style={{ background: "var(--bg-elevated)" }}>
              <div className="flex items-center gap-2 mb-1.5">
                <BookOpen className="w-4 h-4" style={{ color: "var(--accent-amber)" }} />
                <span className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--accent-amber)" }}>
                  La Storia Insegna
                </span>
              </div>
              <h4 className="font-display text-sm font-bold mb-1" style={{ color: "var(--text-primary)" }}>{dd.history.title}</h4>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{dd.history.body}</p>
            </section>
          )}

          <button
            onClick={() => onAsk(item)}
            className="btn-primary w-full justify-center"
          >
            <Sparkles className="w-4 h-4" />
            Chiedi al Copilot IA
          </button>

          {item.url && (
            <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn-ghost w-full justify-center text-xs" data-testid="open-source-article">
              Leggi l'articolo originale
            </a>
          )}

          <p className="text-[10px] text-center" style={{ color: "var(--text-muted)" }}>
            Fonti: {item.sources?.join(" · ")}{item.enriched === false ? " · sintesi automatica senza analisi AI" : ""}
          </p>
        </div>
      </div>
    </div>
  );
};
