import { Home, LineChart, Globe2, GraduationCap, Sparkles } from "lucide-react";

const tabs = [
  { id: "home", label: "Briefing", icon: Home, testId: "nav-tab-home" },
  { id: "markets", label: "Mercati", icon: LineChart, testId: "nav-tab-markets" },
  { id: "radar", label: "Radar", icon: Globe2, testId: "nav-tab-radar" },
  { id: "learn", label: "Impara", icon: GraduationCap, testId: "nav-tab-learn" },
  { id: "copilot", label: "Copilot", icon: Sparkles, testId: "nav-tab-copilot" },
];

export const BottomNav = ({ active, setActive }) => (
  <nav
    data-testid="bottom-nav"
    className="glass-bottom fixed bottom-0 left-0 right-0 z-40"
    style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
  >
    <div className="flex items-stretch justify-around px-1 pt-2 pb-2">
      {tabs.map((t) => {
        const Icon = t.icon;
        const isActive = active === t.id;
        return (
          <button
            key={t.id}
            data-testid={t.testId}
            onClick={() => setActive(t.id)}
            className="flex-1 flex flex-col items-center gap-0.5 py-1.5 rounded-xl transition-all"
            style={{ color: isActive ? "var(--accent-amber)" : "var(--text-muted)" }}
          >
            <Icon className="w-5 h-5" strokeWidth={isActive ? 2.5 : 1.8} />
            <span className="text-[9px] font-semibold tracking-wide font-mono uppercase">{t.label}</span>
          </button>
        );
      })}
    </div>
  </nav>
);
