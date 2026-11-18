import { createContext, useContext, useEffect, useState, useCallback } from "react";

const ThemeCtx = createContext({ theme: "dark", setTheme: () => {} });
const KEY = "flashpulse-theme";

const applyTheme = (t) => {
  const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
  const effective = t === "auto" ? (prefersLight ? "light" : "dark") : t;
  document.documentElement.classList.toggle("light", effective === "light");
  document.documentElement.classList.toggle("dark", effective === "dark");
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", effective === "light" ? "#F8F9FA" : "#08090A");
};

export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(() => localStorage.getItem(KEY) || "auto");

  const setTheme = useCallback((t) => {
    localStorage.setItem(KEY, t);
    setThemeState(t);
    applyTheme(t);
  }, []);

  useEffect(() => {
    applyTheme(theme);
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    const onChange = () => theme === "auto" && applyTheme("auto");
    mq.addEventListener?.("change", onChange);
    return () => mq.removeEventListener?.("change", onChange);
  }, [theme]);

  return <ThemeCtx.Provider value={{ theme, setTheme }}>{children}</ThemeCtx.Provider>;
};

export const useTheme = () => useContext(ThemeCtx);
