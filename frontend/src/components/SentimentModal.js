import { Modal } from "./Modal";
import { Gauge } from "lucide-react";

const bucket = (v) => {
  if (v < 25) return { label: "Paura estrema", color: "var(--bearish)", meaning: "Il mercato è in modalità panico: volatilità alta, flussi verso bond e oro. Storicamente i momenti di paura estrema sono stati anche quelli in cui le aspettative erano al minimo." };
  if (v < 45) return { label: "Paura", color: "#F97316", meaning: "Prevalenza di pessimismo. I prezzi iniziano a scontare scenari negativi: chi investe a lungo termine spesso inizia a guardare con più attenzione le aziende di qualità." };
  if (v < 55) return { label: "Neutrale", color: "var(--accent-amber)", meaning: "Equilibrio tra tori e orsi. I movimenti sono guidati dai fondamentali più che dall'emozione." };
  if (v < 75) return { label: "Avidità", color: "#A3E635", meaning: "Prevalenza di ottimismo. I prezzi cominciano a scontare scenari già positivi: conviene essere prudenti sulle grandi scommesse." };
  return { label: "Avidità estrema", color: "var(--bullish)", meaning: "Euforia di mercato: tutti comprano, la volatilità scende ai minimi. Storicamente è un segnale di cautela, perché i rendimenti futuri migliori sono arrivati più spesso dopo i picchi di paura che dopo quelli di euforia." };
};

export const SentimentModal = ({ open, onClose, value, source }) => {
  const b = bucket(value ?? 50);
  return (
    <Modal open={open} onClose={onClose} title="Sentiment Mercato" subtitle="Fear & Greed Index">
      <div className="space-y-4">
        <div className="card p-4 text-center">
          <Gauge className="w-8 h-8 mx-auto mb-2" style={{ color: b.color }} />
          <div className="font-display text-4xl font-bold" style={{ color: b.color }}>{value ?? 50}/100</div>
          <div className="font-mono text-xs uppercase tracking-wider font-bold mt-1" style={{ color: b.color }}>{b.label}</div>
        </div>
        <div className="h-2 rounded-full overflow-hidden" style={{ background: "var(--bg-elevated)" }}>
          <div className="h-full" style={{ width: `${value}%`, background: `linear-gradient(90deg, var(--bearish), var(--accent-amber), var(--bullish))` }} />
        </div>
        <section>
          <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-1" style={{ color: "var(--text-muted)" }}>Cosa significa oggi</h4>
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{b.meaning}</p>
        </section>
        <section className="card p-3" style={{ background: "var(--bg-elevated)" }}>
          <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-1" style={{ color: "var(--accent-amber)" }}>Come si calcola</h4>
          <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {source === "cnn"
              ? "Fear & Greed Index di CNN: combina 7 misure (volatilità, momentum, ampiezza, put/call, domanda di bond, junk bond, safe-haven). 0 = panico totale, 100 = euforia."
              : "Il dato ufficiale non è raggiungibile: questa è una stima calcolata dalla variazione media degli indici di oggi. 0 = panico totale, 100 = euforia."}
          </p>
        </section>
        <section>
          <h4 className="font-mono text-[10px] uppercase tracking-wider font-bold mb-1" style={{ color: "var(--text-muted)" }}>Regola spannometrica</h4>
          <ul className="text-xs leading-relaxed space-y-1" style={{ color: "var(--text-secondary)" }}>
            <li>• Sotto 25 → paura estrema: spesso i prezzi sono già molto scontati</li>
            <li>• 40-60 → mercato in equilibrio</li>
            <li>• Sopra 75 → euforia: storicamente un segnale di cautela</li>
            <li className="italic">Contenuto educativo, non è un consiglio di investimento.</li>
          </ul>
        </section>
      </div>
    </Modal>
  );
};
