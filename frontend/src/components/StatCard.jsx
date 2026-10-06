import React from "react";

export function StatCard({ title, value, subtitle, icon: Icon, color = "violet", badge }) {
  const colorMap = {
    violet: "text-[#8B5CF6] bg-violet-500/10 border-violet-500/20",
    blue: "text-[#8B5CF6] bg-violet-500/10 border-violet-500/20",
    indigo: "text-[#6366F1] bg-indigo-500/10 border-indigo-500/20",
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    purple: "text-[#8B5CF6] bg-violet-500/10 border-violet-500/20",
  };

  const styleClasses = colorMap[color] || colorMap.violet;

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 shadow-sm hover:border-zinc-700 transition">
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium text-zinc-400 tracking-wide uppercase">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${styleClasses}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold text-white tracking-tight">{value ?? "—"}</span>
        {badge && (
          <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-[#27272A] text-zinc-300 border border-zinc-700">
            {badge}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-zinc-500">{subtitle}</p>}
    </div>
  );
}
