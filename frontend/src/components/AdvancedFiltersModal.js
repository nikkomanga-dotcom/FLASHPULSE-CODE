import { useEffect, useState } from "react";
import { Modal } from "./Modal";
import { Filter, Calendar, Target, Tag } from "lucide-react";
import { fetchNewsTags } from "../lib/api";

const RANGES = [
  { id: 6, label: "6h" }, { id: 24, label: "24h" }, { id: 72, label: "3g" }, { id: 168, label: "7g" }, { id: 0, label: "Tutte" }
];
const CATS = [
  { id: "all", label: "Tutte" }, { id: "macro", label: "Macro" }, { id: "markets", label: "Mercati" }, { id: "geopolitics", label: "Geopolitica" }, { id: "energy", label: "Energia" },
];

export const AdvancedFiltersModal = ({ open, onClose, filters, setFilters }) => {
  const [tags, setTags] = useState([]);
  useEffect(() => { if (open) fetchNewsTags().then((d) => setTags(d?.tags || [])).catch(() => {}); }, [open]);
  const update = (patch) => setFilters({ ...filters, ...patch });
  const toggleTag = (t) => {
    const cur = new Set(filters.tags);
    if (cur.has(t)) cur.delete(t); else cur.add(t);
    update({ tags: [...cur] });
  };
  const reset = () => setFilters({ category: "all", minImpact: 0, maxImpact: 10, sinceHours: 0, tags: [] });
  return (
    <Modal open={open} onClose={onClose} title="Ricerca avanzata" subtitle="Filtra il feed">
      <div className="space-y-5">
        <section>
          <div className="flex items-center gap-2 mb-2"><Calendar className="w-3.5 h-3.5" style={{ color: "var(--accent-amber)" }} /><h4 className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--text-muted)" }}>Periodo</h4></div>
          <div className="flex flex-wrap gap-2">
            {RANGES.map((r) => (
              <button key={r.id} onClick={() => update({ sinceHours: r.id })} data-testid={`filter-since-${r.id}`}
                className="px-3 py-1.5 rounded-full text-xs font-semibold"
                style={{ border: "1px solid var(--border)", background: filters.sinceHours === r.id ? "var(--accent-amber)" : "transparent", color: filters.sinceHours === r.id ? "#0A0A0A" : "var(--text-secondary)" }}>
                {r.label}
              </button>
            ))}
          </div>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-2"><Filter className="w-3.5 h-3.5" style={{ color: "var(--accent-amber)" }} /><h4 className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--text-muted)" }}>Settore</h4></div>
          <div className="flex flex-wrap gap-2">
            {CATS.map((c) => (
              <button key={c.id} onClick={() => update({ category: c.id })}
                className="px-3 py-1.5 rounded-full text-xs font-semibold"
                style={{ border: "1px solid var(--border)", background: filters.category === c.id ? "var(--accent-amber)" : "transparent", color: filters.category === c.id ? "#0A0A0A" : "var(--text-secondary)" }}>
                {c.label}
              </button>
            ))}
          </div>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-2"><Target className="w-3.5 h-3.5" style={{ color: "var(--accent-amber)" }} /><h4 className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--text-muted)" }}>Impact Score</h4></div>
          <div className="flex items-center gap-3 mb-1">
            <span className="font-mono text-[11px]" style={{ color: "var(--text-muted)" }}>min {filters.minImpact}</span>
            <input type="range" min={0} max={10} value={filters.minImpact} onChange={(e) => update({ minImpact: parseInt(e.target.value) })} className="flex-1" />
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[11px]" style={{ color: "var(--text-muted)" }}>max {filters.maxImpact}</span>
            <input type="range" min={0} max={10} value={filters.maxImpact} onChange={(e) => update({ maxImpact: parseInt(e.target.value) })} className="flex-1" />
          </div>
        </section>

        {tags.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-2"><Tag className="w-3.5 h-3.5" style={{ color: "var(--accent-amber)" }} /><h4 className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color: "var(--text-muted)" }}>Tag</h4></div>
            <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto">
              {tags.map((t) => {
                const active = filters.tags.includes(t);
                return (
                  <button key={t} onClick={() => toggleTag(t)}
                    className="chip"
                    style={{ color: active ? "#0A0A0A" : "var(--accent-indigo)", background: active ? "var(--accent-amber)" : "transparent", borderColor: active ? "var(--accent-amber)" : "var(--border)" }}>
                    #{t}
                  </button>
                );
              })}
            </div>
          </section>
        )}

        <div className="flex gap-2">
          <button onClick={reset} className="btn-ghost flex-1 justify-center">Reset</button>
          <button onClick={onClose} className="btn-primary flex-1 justify-center">Applica</button>
        </div>
      </div>
    </Modal>
  );
};
