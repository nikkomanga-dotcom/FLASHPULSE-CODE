import { TrendingUp, TrendingDown } from "lucide-react";

const Spark = ({ data, up }) => {
  if (!data?.length) return null;
  const min = Math.min(...data), max = Math.max(...data);
  const w = 60, h = 20;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / (max - min || 1)) * h;
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg width={w} height={h} className="overflow-visible">
      <polyline
        points={pts}
        fill="none"
        stroke={up ? "var(--bullish)" : "var(--bearish)"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export const MarketWidget = ({ m }) => {
  const up = m.change_pct >= 0;
  return (
    <div className="card p-3 min-w-[140px] flex-shrink-0" data-testid={`market-widget-${m.id}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-mono text-[11px] font-bold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>{m.symbol}</span>
        {up ? <TrendingUp className="w-3.5 h-3.5 price-up" /> : <TrendingDown className="w-3.5 h-3.5 price-down" />}
      </div>
      <div className="font-display text-lg font-bold leading-none mb-1" style={{ color: "var(--text-primary)" }}>
        {m.price.toLocaleString("it-IT", { maximumFractionDigits: m.price > 100 ? 0 : 2 })}
      </div>
      <div className="flex items-center justify-between">
        <span className={`font-mono text-xs font-semibold ${up ? "price-up" : "price-down"}`}>
          {up ? "+" : ""}{m.change_pct.toFixed(2)}%
        </span>
        <Spark data={m.spark} up={up} />
      </div>
    </div>
  );
};
