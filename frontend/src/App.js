import { useEffect, useState } from "react";
import "@/App.css";
import { ThemeProvider } from "./lib/theme";
import { WatchlistProvider } from "./lib/watchlist";
import { TopBar } from "./components/TopBar";
import { BottomNav } from "./components/BottomNav";
import { DeepDiveModal } from "./components/DeepDiveModal";
import { Briefing } from "./pages/Briefing";
import { Markets } from "./pages/Markets";
import { Radar } from "./pages/Radar";
import { Learn } from "./pages/Learn";
import { Copilot } from "./pages/Copilot";

function Shell() {
  const [tab, setTab] = useState("home");
  const [query, setQuery] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [deepDive, setDeepDive] = useState(null);
  const [askSeed, setAskSeed] = useState(null);
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const on = () => setOffline(false);
    const off = () => setOffline(true);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);

  const doRefresh = () => {
    setRefreshing(true);
    setRefreshKey((k) => k + 1);
    setTimeout(() => setRefreshing(false), 600);
  };

  const onAsk = (newsItem) => {
    setDeepDive(null);
    setAskSeed(newsItem);
    setTab("copilot");
  };

  const topBarVisible = tab !== "copilot";

  return (
    <div className="App min-h-[100dvh]">
      {offline && <div className="offline-banner">Sei offline — mostriamo l'ultimo briefing caricato</div>}
      {topBarVisible && <TopBar query={query} setQuery={setQuery} onRefresh={doRefresh} refreshing={refreshing} />}
      <main className="app-safe-bottom">
        {tab === "home" && <Briefing query={query} onOpen={setDeepDive} onAsk={onAsk} refreshKey={refreshKey} />}
        {tab === "markets" && <Markets refreshKey={refreshKey} onAsk={onAsk} />}
        {tab === "radar" && <Radar onAsk={onAsk} refreshKey={refreshKey} />}
        {tab === "learn" && <Learn onAsk={onAsk} />}
        {tab === "copilot" && (
          <Copilot seedContext={askSeed} onContextConsumed={() => setAskSeed(null)} />
        )}
      </main>
      <BottomNav active={tab} setActive={setTab} />
      <DeepDiveModal item={deepDive} onClose={() => setDeepDive(null)} onAsk={onAsk} />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <WatchlistProvider>
        <Shell />
      </WatchlistProvider>
    </ThemeProvider>
  );
}
