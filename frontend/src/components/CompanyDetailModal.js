import { useEffect, useState } from "react";
import { Modal } from "./Modal";
import { TrendingUp, TrendingDown, Minus, Star, Target, Trash2 } from "lucide-react";
import { fetchBigTechDetail, createForecast, fetchForecasts, deleteForecast } from "../lib/api";
import { deviceId } from "../lib/device";
import { useWatchlist } from "../lib/watchlist";

const DIRS = [
  { id: "bullish", label: "Rialzista", icon: TrendingUp, color: "var(--bullish)" },
  { id: "neutral", label: "Neutrale", icon: Minus, color: "var(--text-muted)" },
  { id: "bearish", label: "Ribassista", icon: TrendingDown, color: "var(--bearish)" },
];

export const CompanyDetailModal = ({ ticker, onClose, onAsk }) => {
  const { tickers, toggleTicker } = useWatchlist();
  const [data, setData] = useState(null);
  const [forecasts, setForecasts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [dir, setDir] = useState("bullish");
  const [price, setPrice] = useState("");
  const [horizon, setHorizon] = useState(6);
  const [thesis, setThesis] = useState("");
  const [saveError, setSaveError] = useState("");
  useEffect(() => {
    if (!ticker) return;
    let a = true;
    setData(null); setForecasts([]); setShowForm(false); setSaveError("");
    fetchBigTechDetail(ticker).then((d) => { if (a) setData(d); }).catch(() => {});
    fetchForecasts(deviceId()).then((d) => { if (a) setForecasts((d?.forecasts || []).filter((f) => f.ticker === ticker)); }).catch(() => {});
    return () => { a = false; };
  }, [ticker]);
  if (!ticker) return null;
  const inWatchlist = tickers.includes(ticker);

  const save = async () => {
    if (!thesis.trim()) return;
    setSaveError("");
    try {
      await createForecast({
        device_id: deviceId(), ticker, direction: dir,
        target_price: price ? parseFloat(price) : null, horizon_months: horizon, thesis: thesis.trim(),
      });
    } catch {
      setSaveError("Non sono riuscito a salvare la previsione. Controlla i campi e riprova.");
      return;
    }
    const upd = await fetchForecasts(deviceId());
    setForecasts((upd?.forecasts || []).filter((f) => f.ticker === ticker));
    setShowForm(false); setThesis(""); setPrice(""); setDir("bullish"); setHorizon(6);
  };

  const remove = async () => {
    try { await deleteForecast(ticker, deviceId()); setForecasts([]); } catch {}
  };

  return (
    <Modal open={!!ticker} onClose={onClose} title={`${ticker} · ${data?.name || ""}`} subtitle={data?.sector}>
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-mono font-bold" style={{ color: "var(--text-primary)" }}>Ricavi TTM {data?.revenue_ttm ?? "n/d"}{data?.revenue_ttm != null ? "B" : ""}</span>
            {data?.revenue_growth != null && (
              <span className={`font-mono font-bold ${data.revenue_growth >= 0 ? "price-up" : "price-down"}`}>
                {data.revenue_growth >= 0 ? "+" : ""}{data.revenue_growth}%
              </span>
            )}
            <span className="font-mono" style={{ color: "var(--text-muted)" }}>P/E {data?.pe ?? "n/d"}</span>
          </div>
          <button onClick={() => toggleTicker(ticker)} className="btn-ghost !p-2" title="Preferito">
            <Star className="w-4 h-4" style={{ color: inWatchlist ? "var(--accent-amber)" : "var(--text-muted)", fill: inWatchlist ? "var(--accent-amber)" : "none" }} />
          </button>
        </div>

        <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{data?.description}</p>
        {data && (
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
            {data.fundamentals_source === "live" ? "Ricavi, crescita e P/E: dati aggiornati (Finnhub / Alpha Vantage)." : "Ricavi, crescita e P/E: valori di riferimento, il servizio dati non risponde."} Descrizione e giudizio sono editoriali.
          </p>
        )}

        {data?.revenue_breakdown && (
          <section>
            <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-2" style={{ color: "var(--text-muted)" }}>Ricavi per segmento</h4>
            <div className="space-y-1.5">
              {data.revenue_breakdown.map((s) => (
                <div key={s.seg} className="flex items-center gap-2">
                  <span className="text-xs w-32 shrink-0" style={{ color: "var(--text-secondary)" }}>{s.seg}</span>
                  <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--bg-elevated)" }}>
                    <div className="h-full" style={{ width: `${s.pct}%`, background: "var(--accent-amber)" }} />
                  </div>
                  <span className="font-mono text-[11px] font-bold" style={{ color: "var(--text-primary)" }}>{s.pct}%</span>
                </div>
              ))}
            </div>
          </section>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div className="card p-3">
            <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-1 price-up">Catalyst</h4>
            <ul className="text-xs space-y-1" style={{ color: "var(--text-secondary)" }}>
              {(data?.catalysts || []).map((c) => <li key={c}>• {c}</li>)}
            </ul>
          </div>
          <div className="card p-3">
            <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-1 price-down">Rischi</h4>
            <ul className="text-xs space-y-1" style={{ color: "var(--text-secondary)" }}>
              {(data?.risks || []).map((r) => <li key={r}>• {r}</li>)}
            </ul>
          </div>
        </div>

        {/* User forecasts */}
        <section>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4" style={{ color: "var(--accent-amber)" }} />
              <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--text-muted)" }}>La tua previsione</h4>
            </div>
            {forecasts.length === 0 && !showForm && (
              <button onClick={() => setShowForm(true)} data-testid="create-forecast-btn" className="btn-ghost !py-1 !px-2 text-xs">+ Crea</button>
            )}
            {forecasts.length > 0 && (
              <button onClick={remove} className="btn-ghost !p-2" aria-label="Rimuovi"><Trash2 className="w-3.5 h-3.5" style={{ color: "var(--bearish)" }} /></button>
            )}
          </div>
          {forecasts.map((f) => (
            <div key={f.created_at} className="card p-3">
              <div className="flex items-center gap-2 mb-1.5">
                {f.direction === "bullish" && <TrendingUp className="w-4 h-4 price-up" />}
                {f.direction === "bearish" && <TrendingDown className="w-4 h-4 price-down" />}
                {f.direction === "neutral" && <Minus className="w-4 h-4" style={{ color: "var(--text-muted)" }} />}
                <span className="font-mono text-xs font-bold" style={{ color: "var(--text-primary)" }}>{f.direction.toUpperCase()}</span>
                {f.target_price && <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>· Target ${f.target_price}</span>}
                <span className="font-mono text-[10px] ml-auto" style={{ color: "var(--text-muted)" }}>{f.horizon_months}m</span>
              </div>
              <p className="text-xs" style={{ color: "var(--text-secondary)" }}>{f.thesis}</p>
            </div>
          ))}
          {showForm && (
            <div className="card p-3 space-y-2">
              <div className="flex gap-1.5">
                {DIRS.map((d) => {
                  const Icon = d.icon;
                  return (
                    <button key={d.id} onClick={() => setDir(d.id)}
                      className="flex-1 py-2 rounded-lg flex flex-col items-center gap-1"
                      style={{ background: dir === d.id ? "var(--bg-elevated)" : "transparent", border: `1px solid ${dir === d.id ? d.color : "var(--border)"}`, color: d.color }}>
                      <Icon className="w-4 h-4" />
                      <span className="text-[10px] font-mono font-bold">{d.label}</span>
                    </button>
                  );
                })}
              </div>
              <div className="flex gap-2">
                <input value={price} onChange={(e) => setPrice(e.target.value)} placeholder="Target $ (opz.)" type="number" className="flex-1 px-2 py-1.5 rounded-lg text-sm outline-none" style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
                <input value={horizon} onChange={(e) => setHorizon(parseInt(e.target.value) || 1)} type="number" min={1} max={60} className="w-20 px-2 py-1.5 rounded-lg text-sm outline-none" style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
                <span className="text-[11px] self-center" style={{ color: "var(--text-muted)" }}>mesi</span>
              </div>
              <textarea value={thesis} onChange={(e) => setThesis(e.target.value)} placeholder="La tua tesi in una riga…" rows={2} className="w-full px-2 py-1.5 rounded-lg text-sm outline-none" style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
              {saveError && <p className="text-[11px]" style={{ color: "var(--bearish)" }}>{saveError}</p>}
              <div className="flex gap-2">
                <button onClick={() => setShowForm(false)} className="btn-ghost flex-1 justify-center">Annulla</button>
                <button onClick={save} data-testid="save-forecast-btn" className="btn-primary flex-1 justify-center">Salva</button>
              </div>
            </div>
          )}
        </section>

        <button onClick={() => { onAsk({ title: `${ticker} ${data?.name}`, bullets: [data?.description || ""], impact: 7, tags: [`#${ticker}`], domino: (data?.catalysts || []).join(" · ") }); onClose(); }} className="btn-primary w-full justify-center">
          Chiedi al Copilot IA un'analisi su {ticker}
        </button>
      </div>
    </Modal>
  );
};
