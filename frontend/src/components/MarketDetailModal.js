import { useEffect, useState } from "react";
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Modal } from "./Modal";
import { fetchChart } from "../lib/api";
import { TrendingUp, TrendingDown } from "lucide-react";

const RANGES = [{ id: 7, label: "1S" }, { id: 30, label: "1M" }, { id: 90, label: "3M" }, { id: 365, label: "1A" }];

export const MarketDetailModal = ({ market, onClose }) => {
  const [series, setSeries] = useState([]);
  const [range, setRange] = useState(30);
  const [error, setError] = useState(false);
  useEffect(() => {
    if (!market) return;
    let a = true;
    setError(false);
    setSeries([]);
    fetchChart(market.id, range).then((d) => { if (a) setSeries(d?.series || []); }).catch(() => { if (a) setError(true); });
    return () => { a = false; };
  }, [market, range]);
  if (!market) return null;
  const up = market.change_pct >= 0;
  return (
    <Modal open={!!market} onClose={onClose} title={market.name} subtitle={`${market.symbol} · ${market.currency}`} size="md">
      <div className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <div className="font-display text-3xl font-bold" style={{ color: "var(--text-primary)" }}>
              {market.price.toLocaleString("it-IT", { maximumFractionDigits: 2 })}
            </div>
            <div className={`flex items-center gap-1 font-mono text-sm font-bold ${up ? "price-up" : "price-down"}`}>
              {up ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {up ? "+" : ""}{market.change_pct.toFixed(2)}%
            </div>
          </div>
          <div className="flex gap-1">
            {RANGES.map((r) => (
              <button key={r.id} onClick={() => setRange(r.id)}
                className="px-2 py-1 rounded-md text-[10px] font-mono font-bold"
                style={{
                  background: range === r.id ? "var(--accent-amber)" : "transparent",
                  color: range === r.id ? "#0A0A0A" : "var(--text-muted)",
                  border: "1px solid var(--border)",
                }}>{r.label}</button>
            ))}
          </div>
        </div>
        {error && <p className="text-xs" style={{ color: "var(--text-muted)" }}>Storico non disponibile al momento.</p>}
        <div style={{ width: "100%", height: 180 }}>
          <ResponsiveContainer>
            <AreaChart data={series} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="mdm-g" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--accent-amber)" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="var(--accent-amber)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="t" hide />
              <YAxis hide domain={["dataMin", "dataMax"]} />
              <Tooltip
                contentStyle={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 11 }}
                labelStyle={{ color: "var(--text-muted)" }}
              />
              <Area type="monotone" dataKey="v" stroke="var(--accent-amber)" strokeWidth={2} fill="url(#mdm-g)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="card p-3">
            <div className="text-[10px] font-mono uppercase tracking-wider mb-1" style={{ color: "var(--text-muted)" }}>Variazione</div>
            <div className={`font-mono text-sm font-bold ${up ? "price-up" : "price-down"}`}>{up ? "+" : ""}{market.change.toFixed(2)}</div>
          </div>
          <div className="card p-3">
            <div className="text-[10px] font-mono uppercase tracking-wider mb-1" style={{ color: "var(--text-muted)" }}>Fonte quotazione</div>
            <div className="font-mono text-xs font-bold" style={{ color: "var(--text-primary)" }}>{market.source || "n/d"}</div>
          </div>
        </div>
        <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
          Quotazioni da Yahoo Finance (aggiornate ogni ~5 minuti, possono avere qualche minuto di ritardo). {market.stale ? "Il servizio non risponde: stai vedendo l'ultimo dato noto." : ""}
        </p>
      </div>
    </Modal>
  );
};
