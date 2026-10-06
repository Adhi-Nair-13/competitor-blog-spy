import React from "react";
import { Loader2, AlertCircle } from "lucide-react";

export function StatusBadge({ status }) {
  const norm = (status || "").toUpperCase();

  switch (norm) {
    case "ONLINE":
    case "SUCCESS":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          {norm === "ONLINE" ? "Online" : "Success"}
        </span>
      );

    case "CHECKING":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20">
          <Loader2 className="w-3 h-3 animate-spin text-[#8B5CF6]" />
          Checking
        </span>
      );

    case "ERROR":
    case "FAILED":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
          {norm === "ERROR" ? "Error" : "Failed"}
        </span>
      );

    case "DISABLED":
    case "OFFLINE":
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#27272A] text-zinc-400 border border-zinc-700">
          <span className="h-2 w-2 rounded-full bg-zinc-500"></span>
          {norm || "Disabled"}
        </span>
      );
  }
}
