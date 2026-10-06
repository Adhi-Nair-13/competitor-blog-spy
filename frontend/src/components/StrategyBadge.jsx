import React from "react";
import { Rss, FileCode2, Globe, Layers } from "lucide-react";

export function StrategyBadge({ strategy }) {
  const s = strategy || "Automatic";

  if (s.includes("RSS") && s.includes("Sitemap")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20">
        <Layers className="w-3.5 h-3.5 text-[#8B5CF6]" />
        RSS + Sitemap
      </span>
    );
  }

  if (s.includes("RSS")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
        <Rss className="w-3.5 h-3.5 text-amber-400" />
        RSS / Atom
      </span>
    );
  }

  if (s.includes("Sitemap")) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-500/10 text-[#6366F1] border border-indigo-500/20">
        <FileCode2 className="w-3.5 h-3.5 text-[#6366F1]" />
        Sitemap
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20">
      <Globe className="w-3.5 h-3.5 text-[#8B5CF6]" />
      {s || "Direct Page"}
    </span>
  );
}
