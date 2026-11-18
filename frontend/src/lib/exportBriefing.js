import jsPDF from "jspdf";
import { fetchNews, fetchMarkets, fetchHistoryToday } from "./api";

// jsPDF's built-in Helvetica only covers Latin-1: swap the few common symbols that fall outside it.
const pdfSafe = (s) =>
  String(s ?? "")
    .replace(/[→⇒➜➔]/g, "->").replace(/[←]/g, "<-").replace(/≥/g, ">=").replace(/≤/g, "<=")
    .replace(/[“”„]/g, '"').replace(/[‘’]/g, "'").replace(/[–—]/g, "-").replace(/…/g, "...")
    .replace(/[\u2000-\u2021\u2023-\u206F\u2190-\u21FF\u2200-\u22FF\u{1F000}-\u{1FFFF}\u2600-\u27BF\uFE0F]/gu, "")
    .replace(/\s{2,}/g, " ");

const nowLabel = () => {
  const d = new Date();
  return d.toLocaleString("it-IT", { dateStyle: "long", timeStyle: "short" });
};

export const exportBriefingPDF = async () => {
  const [newsData, mkt, pill] = await Promise.all([fetchNews({}), fetchMarkets().catch(() => null), fetchHistoryToday().catch(() => null)]);
  const news = (newsData?.items || []).slice(0, 8);
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const W = doc.internal.pageSize.getWidth();
  let y = 48;

  doc.setFillColor(8, 9, 10);
  doc.rect(0, 0, W, 90, "F");
  doc.setTextColor(245, 158, 11);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.text("FlashPulse · Briefing", 48, 50);
  doc.setFontSize(10);
  doc.setTextColor(200, 200, 200);
  doc.text(nowLabel(), 48, 70);

  y = 120;
  doc.setTextColor(17, 24, 39);
  doc.setFontSize(13);
  doc.setFont("helvetica", "bold");
  doc.text("Indici & Asset", 48, y);
  y += 14;
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  (mkt?.markets || []).forEach((m) => {
    const sign = m.change_pct >= 0 ? "+" : "";
    doc.setTextColor(17, 24, 39);
    doc.text(pdfSafe(m.symbol), 48, y);
    doc.text(pdfSafe(m.price.toLocaleString("it-IT")), 180, y);
    doc.setTextColor(m.change_pct >= 0 ? 5 : 220, m.change_pct >= 0 ? 150 : 38, m.change_pct >= 0 ? 105 : 38);
    doc.text(`${sign}${m.change_pct.toFixed(2)}%`, 300, y);
    y += 14;
  });

  y += 10;
  doc.setDrawColor(230);
  doc.line(48, y, W - 48, y);
  y += 18;

  if (pill) {
    doc.setTextColor(217, 119, 6);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(pdfSafe(`${pill.exact ? "ACCADDE OGGI" : "ACCADDE IN QUESTI GIORNI"} · ${pill.date}`), 48, y);
    y += 14;
    doc.setTextColor(17, 24, 39);
    doc.setFontSize(11);
    doc.text(pdfSafe(pill.title), 48, y);
    y += 14;
    doc.setFontSize(9);
    doc.setFont("helvetica", "normal");
    const lines = doc.splitTextToSize(pdfSafe(pill.body), W - 96);
    doc.text(lines, 48, y);
    y += lines.length * 11 + 14;
  }

  doc.setDrawColor(230);
  doc.line(48, y, W - 48, y);
  y += 18;

  doc.setTextColor(17, 24, 39);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.text("Notizie del giorno", 48, y);
  y += 16;

  for (const n of news) {
    if (y > 760) { doc.addPage(); y = 48; }
    const badge = `IMPACT ${n.impact}/10`;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.setTextColor(n.impact >= 8 ? 220 : n.impact >= 5 ? 217 : 34, n.impact >= 8 ? 38 : n.impact >= 5 ? 119 : 150, n.impact >= 8 ? 38 : n.impact >= 5 ? 6 : 150);
    doc.text(badge, 48, y);
    doc.setTextColor(107, 114, 128);
    doc.setFont("helvetica", "normal");
    doc.text(pdfSafe(`[${(n.sources || []).join(", ")}]`), 120, y);
    y += 14;

    doc.setTextColor(17, 24, 39);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    const title = doc.splitTextToSize(pdfSafe(n.title), W - 96);
    doc.text(title, 48, y);
    y += title.length * 13 + 4;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9.5);
    (n.bullets || []).forEach((b) => {
      if (y > 780) { doc.addPage(); y = 48; }
      const lines = doc.splitTextToSize(pdfSafe(`• ${b}`), W - 110);
      doc.text(lines, 62, y);
      y += lines.length * 11;
    });
    doc.setTextColor(79, 70, 229);
    doc.setFontSize(8.5);
    doc.text(pdfSafe((n.tags || []).join("  ")), 48, y + 8);
    y += 18;
    doc.setTextColor(17, 24, 39);
    doc.setFont("helvetica", "italic");
    doc.setFontSize(9);
    if (n.domino) {
      const dLines = doc.splitTextToSize(pdfSafe(`Effetto domino: ${n.domino}`), W - 96);
      doc.text(dLines, 48, y);
      y += dLines.length * 11 + 14;
    } else {
      y += 6;
    }
    doc.setFont("helvetica", "normal");
    doc.setDrawColor(240);
    doc.line(48, y - 6, W - 48, y - 6);
    y += 6;
  }

  doc.save(`flashpulse-briefing-${new Date().toISOString().slice(0, 10)}.pdf`);
};
