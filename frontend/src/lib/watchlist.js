import { createContext, useContext, useEffect, useState, useCallback } from "react";

const Ctx = createContext({ tickers: [], regions: [], toggleTicker: () => {}, toggleRegion: () => {} });
const KEY = "flashpulse-watchlist-v1";

export const WatchlistProvider = ({ children }) => {
  const [state, setState] = useState({ tickers: [], regions: [] });
  useEffect(() => {
    try { const s = JSON.parse(localStorage.getItem(KEY) || "{}"); setState({ tickers: s.tickers || [], regions: s.regions || [] }); } catch {}
  }, []);
  const persist = (next) => { setState(next); localStorage.setItem(KEY, JSON.stringify(next)); };
  const toggleTicker = useCallback((t) => setState((s) => {
    const next = { ...s, tickers: s.tickers.includes(t) ? s.tickers.filter((x) => x !== t) : [...s.tickers, t] };
    localStorage.setItem(KEY, JSON.stringify(next));
    return next;
  }), []);
  const toggleRegion = useCallback((r) => setState((s) => {
    const next = { ...s, regions: s.regions.includes(r) ? s.regions.filter((x) => x !== r) : [...s.regions, r] };
    localStorage.setItem(KEY, JSON.stringify(next));
    return next;
  }), []);
  const clear = useCallback(() => persist({ tickers: [], regions: [] }), []);
  return <Ctx.Provider value={{ ...state, toggleTicker, toggleRegion, clear }}>{children}</Ctx.Provider>;
};

export const useWatchlist = () => useContext(Ctx);
