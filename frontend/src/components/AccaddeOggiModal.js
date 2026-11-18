import { useEffect, useState } from "react";
import { Modal } from "./Modal";
import { BookOpen } from "lucide-react";
import { fetchHistoryCuriosities } from "../lib/api";

export const AccaddeOggiModal = ({ open, onClose, pill }) => {
  const [items, setItems] = useState([]);
  useEffect(() => {
    if (!open) return;
    fetchHistoryCuriosities().then((d) => setItems(d?.items || [])).catch(() => {});
  }, [open]);
  return (
    <Modal open={open} onClose={onClose} title={pill?.exact === false ? "Accadde in questi giorni" : "Accadde oggi nei mercati"} subtitle="Curiosità storiche">
      {pill && (
        <section className="card p-4 mb-4" style={{ background: "var(--bg-elevated)" }} data-testid="accadde-oggi-main">
          <div className="font-mono text-[11px] mb-1" style={{ color: "var(--accent-amber)" }}>{pill.date}</div>
          <h3 className="font-display text-base font-bold mb-1" style={{ color: "var(--text-primary)" }}>{pill.title}</h3>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{pill.body}</p>
        </section>
      )}
      <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-2" style={{ color: "var(--text-muted)" }}>Altre curiosità</h4>
      <div className="space-y-2">
        {items.filter((i) => !pill || i.title !== pill.title).map((i) => (
          <div key={i.title} className="card p-3">
            <div className="flex items-center gap-2 mb-1">
              <BookOpen className="w-3.5 h-3.5" style={{ color: "var(--accent-amber)" }} />
              <span className="font-mono text-[11px]" style={{ color: "var(--text-muted)" }}>{i.date}{i.exact ? " · oggi" : ""}</span>
            </div>
            <h5 className="font-display text-sm font-bold" style={{ color: "var(--text-primary)" }}>{i.title}</h5>
            <p className="text-xs leading-relaxed mt-1" style={{ color: "var(--text-secondary)" }}>{i.body}</p>
          </div>
        ))}
      </div>
    </Modal>
  );
};
