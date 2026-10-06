import React from "react";
import { Bell, RefreshCw, Sparkles } from "lucide-react";

export function Navbar({
  currentTab,
  onOpenNotifications,
  unreadCount,
  onTriggerRunAll,
  isCheckingAll,
  onSeedDemo,
  isSeeding,
  systemStatus
}) {
  const tabTitles = {
    dashboard: "Executive Monitoring Overview",
    competitors: "Competitor Directory & Discovery",
    articles: "Real-Time Ingested Content",
    history: "Detection Audit & Checks Log",
    analytics: "Performance & Strategy Intelligence",
    "scale-test": "100-Website Concurrency Benchmark",
    "demo-control": "Controlled Demo Site & Publication Trigger",
    settings: "System Configuration & Alert Policies",
  };

  return (
    <header className="h-16 bg-[#18181B]/80 backdrop-blur-md border-b border-[#27272A] px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Title */}
      <div>
        <h1 className="text-sm font-bold text-white tracking-tight">
          {tabTitles[currentTab] || "Competitor Content Radar"}
        </h1>
        <p className="text-[11px] text-zinc-400">
          Target: Detection delay &lt; 5 minutes across RSS, Sitemap, and Direct Page DOM.
        </p>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-3">
        {/* System Health indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#27272A]/80 border border-zinc-700/60 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span className="text-zinc-300 font-medium">System:</span>
          <span className="font-semibold text-emerald-400">HEALTHY</span>
        </div>

        {/* 1-Click Demo Competitor Seed Button */}
        <button
          onClick={onSeedDemo}
          disabled={isSeeding}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold hover:bg-emerald-600/30 transition disabled:opacity-50"
          title="Instantly registers http://127.0.0.1:8001/ as a competitor to test live detections!"
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          <span>{isSeeding ? "Seeding..." : "Quick Demo Competitor"}</span>
        </button>

        {/* Run All Checks Trigger */}
        <button
          onClick={onTriggerRunAll}
          disabled={isCheckingAll}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold shadow-md shadow-violet-600/20 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isCheckingAll ? "animate-spin" : ""}`} />
          <span>{isCheckingAll ? "Checking..." : "Run Checks Now"}</span>
        </button>

        {/* Notifications Icon with Badge */}
        <button
          onClick={onOpenNotifications}
          className="relative p-2 rounded-lg bg-[#27272A] border border-zinc-700 text-zinc-300 hover:text-white hover:bg-zinc-700/80 transition"
          title="View notifications"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center animate-bounce">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
}
