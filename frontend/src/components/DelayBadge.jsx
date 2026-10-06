import React from "react";
import { CheckCircle2, AlertTriangle, HelpCircle } from "lucide-react";

export function DelayBadge({ delaySeconds, delayFormatted, showIcon = true }) {
  if (delaySeconds === null || delaySeconds === undefined) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#27272A] text-zinc-400 border border-zinc-700">
        {showIcon && <HelpCircle className="w-3.5 h-3.5 text-zinc-500" />}
        {delayFormatted || "Publication time unavailable"}
      </span>
    );
  }

  const isGreen = delaySeconds <= 300; // <= 5 minutes (300s)

  if (isGreen) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        {showIcon && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
        <span>{delayFormatted}</span>
        <span className="text-[10px] uppercase tracking-wider text-emerald-500/80 font-mono">(≤ 5m)</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
      {showIcon && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
      <span>{delayFormatted}</span>
      <span className="text-[10px] uppercase tracking-wider text-amber-500/80 font-mono">(&gt; 5m)</span>
    </span>
  );
}
