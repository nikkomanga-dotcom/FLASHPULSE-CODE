import { useEffect, useState } from "react";
import { Star, X, Plus } from "lucide-react";
import { useWatchlist } from "../lib/watchlist";

const TICKERS = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "TSLA", "ASML", "AMZN", "AMD", "TSM", "BTC", "WTI"];
const REGIONS = ["USA", "Europa", "Eurozona", "Asia", "Cina", "Medio Oriente"];

export const WatchlistSheet = ({ open, onClose }) => {
  const { tickers, regions, toggleTicker, toggleRegion, clear } = useWatchlist();
  const [customTicker, setCustomTicker] = useState("");
  const [allTickers, setAllTickers] = useState(TICKERS);
  useEffect(() => {
    if (!open) return;
    const extras = tickers.filter((t) => !TICKERS.includes(t));
    setAllTickers([...TICKERS, ...extras]);
  }, [open, tickers]);
  if (!open) return null;

  const addCustom = () => {
    const t = customTicker.trim().toUpperCase();
    if (!t) return;
    if (!tickers.includes(t)) toggleTicker(t);
    setCustomTicker("");
    setAllTickers((prev) => (prev.includes(t) ? prev : [...prev, t]));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center" onClick={onClose} data-testid="watchlist-sheet">
      <div className="absolute inset-0" style={{ background: "rgba(0,0,0,0.65)" }} />
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full sm:max-w-md max-h-[80dvh] overflow-y-auto rounded-t-3xl sm:rounded-3xl"
        style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between px-4 py-3" style={{ background: "var(--bg-surface)", borderBottom: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2">
            <Star className="w-4 h-4" style={{ color: "var(--accent-amber)" }} />
            <span className="font-display text-sm font-bold" style={{ color: "var(--text-primary)" }}>La tua Watchlist</span>
          </div>
          <button onClick={onClose} className="btn-ghost !p-2"><X className="w-4 h-4" /></button>
        </div>
        <div className="px-5 py-4 space-y-4">
          <section>
            <h3 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-2" style={{ color: "var(--text-muted)" }}>Ticker preferiti</h3>
            <div className="flex flex-wrap gap-2 mb-2">
              {allTickers.map((t) => {
                const active = tickers.includes(t);
                return (
                  <button
                    key={t}
                    onClick={() => toggleTicker(t)}
                    data-testid={`watch-ticker-${t}`}
                    className="px-3 py-1.5 rounded-full text-xs font-mono font-bold"
                    style={{
                      border: "1px solid var(--border)",
                      background: active ? "var(--accent-amber)" : "transparent",
                      color: active ? "#0A0A0A" : "var(--text-secondary)",
                    }}
                  >
                    {t}
                  </button>
                );
              })}
            </div>
            <div className="flex gap-2">
              <input
                value={customTicker}
                onChange={(e) => setCustomTicker(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addCustom()}
                placeholder="Aggiungi ticker (es. ENI, UCG)"
                className="flex-1 px-3 py-2 rounded-lg text-sm outline-none"
                style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
              />
              <button onClick={addCustom} className="btn-ghost !p-2"><Plus className="w-4 h-4" /></button>
            </div>
          </section>

          <section>
            <h3 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-2" style={{ color: "var(--text-muted)" }}>Paesi / Regioni</h3>
            <div className="flex flex-wrap gap-2">
              {REGIONS.map((r) => {
                const active = regions.includes(r);
                return (
                  <button
                    key={r}
                    onClick={() => toggleRegion(r)}
                    data-testid={`watch-region-${r}`}
                    className="px-3 py-1.5 rounded-full text-xs font-semibold"
                    style={{
                      border: "1px solid var(--border)",
                      background: active ? "var(--accent-indigo)" : "transparent",
                      color: active ? "#FFFFFF" : "var(--text-secondary)",
                    }}
                  >
                    {r}
                  </button>
                );
              })}
            </div>
          </section>

          <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
            Le notizie che citano un tuo ticker o una tua regione saranno evidenziate in cima al briefing con la stellina.
          </p>

          <button onClick={clear} className="btn-ghost w-full justify-center text-xs">Svuota watchlist</button>
        </div>
      </div>
    </div>
  );
};
