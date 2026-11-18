import { Search, Sun, Moon, Monitor, RefreshCw, Zap, Star, Download, Bell, BellOff } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useTheme } from "../lib/theme";
import { useWatchlist } from "../lib/watchlist";
import { WatchlistSheet } from "./WatchlistSheet";
import { exportBriefingPDF } from "../lib/exportBriefing";
import { enablePush, disablePush, pushEnabledLocal, sendPushTest } from "../lib/push";

export const TopBar = ({ query, setQuery, onRefresh, refreshing }) => {
  const { theme, setTheme } = useTheme();
  const { tickers, regions } = useWatchlist();
  const [wlOpen, setWlOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [pushOn, setPushOn] = useState(false);
  const [pushBusy, setPushBusy] = useState(false);
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);
  const flash = (msg, ms = 3200) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), ms);
  };
  useEffect(() => () => clearTimeout(toastTimer.current), []);
  const cycle = () => setTheme(theme === "dark" ? "light" : theme === "light" ? "auto" : "dark");
  const Icon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;
  const count = tickers.length + regions.length;

  useEffect(() => { setPushOn(pushEnabledLocal()); }, []);

  const doExport = async () => {
    setExporting(true);
    try { await exportBriefingPDF(); } catch { flash("Non sono riuscito a creare il PDF. Riprova tra poco."); }
    setExporting(false);
  };

  const togglePush = async () => {
    setPushBusy(true);
    try {
      if (pushOn) {
        await disablePush();
        setPushOn(false);
        flash("Allerte critiche disattivate");
      } else {
        const r = await enablePush();
        if (r.ok) {
          setPushOn(true);
          await sendPushTest().catch(() => {});
          flash("Allerte critiche attivate ⚡ Impact ≥ 9");
        } else {
          flash(r.message || "Non è stato possibile attivare le notifiche");
        }
      }
    } catch {
      flash("Non è stato possibile cambiare le notifiche. Riprova.");
    }
    setPushBusy(false);
  };

  return (
    <header className="glass sticky top-0 z-40 app-safe-top" data-testid="app-header">
      <div className="px-4 pt-3 pb-2">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: "var(--accent-amber)" }}>
              <Zap className="w-4 h-4" strokeWidth={2.5} color="#0A0A0A" />
            </div>
            <div>
              <div className="font-display text-base font-bold leading-none" style={{ color: "var(--text-primary)" }}>FlashPulse</div>
              <div className="font-mono text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>Briefing finanziario · Live</div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={togglePush} data-testid="push-toggle-button" className="btn-ghost !p-2" disabled={pushBusy} aria-label="Allerte">
              {pushOn ? <Bell className="w-4 h-4" style={{ color: "var(--accent-amber)" }} /> : <BellOff className="w-4 h-4" />}
            </button>
            <button onClick={() => setWlOpen(true)} data-testid="watchlist-button" className="btn-ghost !p-2 relative" aria-label="Watchlist">
              <Star className="w-4 h-4" />
              {count > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[9px] font-mono font-bold flex items-center justify-center" style={{ background: "var(--accent-amber)", color: "#0A0A0A" }}>{count}</span>
              )}
            </button>
            <button onClick={doExport} data-testid="export-briefing-button" className="btn-ghost !p-2" aria-label="Export">
              {exporting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            </button>
            <button onClick={onRefresh} data-testid="refresh-feed-button" className="btn-ghost !p-2" aria-label="Refresh">
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            </button>
            <button onClick={cycle} data-testid="theme-toggle-button" className="btn-ghost !p-2" aria-label="Theme">
              <Icon className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
          <input
            data-testid="universal-search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cerca notizie, ticker, paesi…"
            className="w-full pl-9 pr-3 py-2.5 rounded-xl text-sm outline-none"
            style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-primary)" }}
          />
        </div>
      </div>
      {toast && (
        <div className="px-4 pb-2">
          <div className="text-xs px-3 py-2 rounded-lg" style={{ background: "var(--bg-elevated)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
            {toast}
          </div>
        </div>
      )}
      <WatchlistSheet open={wlOpen} onClose={() => setWlOpen(false)} />
    </header>
  );
};
