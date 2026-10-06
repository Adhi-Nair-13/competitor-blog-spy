import React from "react";
import {
  LayoutDashboard,
  Building2,
  Newspaper,
  History,
  BarChart3,
  Cpu,
  Settings,
  Radio,
  Radar,
  ChevronRight,
} from "lucide-react";

export function Sidebar({ currentTab, setCurrentTab }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "competitors", label: "Competitors", icon: Building2 },
    { id: "articles", label: "Articles", icon: Newspaper },
    { id: "history", label: "Monitoring History", icon: History },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "scale-test", label: "Scale Test (100 Sites)", icon: Cpu, badge: "Benchmark" },
    { id: "demo-control", label: "Demo Controller", icon: Radio, badge: "Live Test" },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#18181B] border-r border-[#27272A] flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-[#27272A]">
        <div className="w-9 h-9 rounded-xl bg-[#8B5CF6] flex items-center justify-center text-white shadow-lg shadow-violet-500/25">
          <Radar className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
            BlogSpy <span className="text-[10px] px-1.5 py-0.2 rounded bg-violet-500/20 text-[#8B5CF6] font-mono">v1.0</span>
          </div>
          <div className="text-[11px] text-zinc-400 font-medium">Competitor Radar</div>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-zinc-500">
          Monitoring Suite
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                isActive
                  ? "bg-[#8B5CF6] text-white shadow-md shadow-violet-600/30"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-[#27272A]/60"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-zinc-400"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge ? (
                <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold uppercase ${
                  isActive ? "bg-white/20 text-white" : "bg-[#27272A] text-zinc-400 border border-zinc-700"
                }`}>
                  {item.badge}
                </span>
              ) : (
                isActive && <ChevronRight className="w-3.5 h-3.5 opacity-70" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#27272A] text-[11px] text-zinc-500 flex items-center justify-between">
        <span className="font-mono">Engine: APScheduler</span>
        <span className="flex items-center gap-1 text-emerald-400 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-ping"></span>
          Active
        </span>
      </div>
    </aside>
  );
}
