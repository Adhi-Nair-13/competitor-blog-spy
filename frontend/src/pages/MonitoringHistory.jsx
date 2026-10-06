import React, { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import { StrategyBadge } from "../components/StrategyBadge";

export function MonitoringHistory() {
  const [history, setHistory] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [competitorFilter, setCompetitorFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [methodFilter, setMethodFilter] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [historyData, compsData] = await Promise.all([
        api.getMonitoringHistory({
          competitor_id: competitorFilter || undefined,
          status: statusFilter || undefined,
          detection_method: methodFilter || undefined,
          limit: 100,
        }),
        api.getCompetitors(),
      ]);
      setHistory(historyData);
      setCompetitors(compsData);
    } catch (err) {
      console.error("Error loading monitoring history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [competitorFilter, statusFilter, methodFilter]);

  return (
    <div className="space-y-6">
      {/* Filters Header */}
      <div className="bg-[#18181B] p-4 rounded-xl border border-[#27272A] flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-tight">Monitoring Checks & Audit Trail</h2>
          <p className="text-xs text-zinc-400">Complete execution history of scheduled and on-demand polling runs</p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={competitorFilter}
            onChange={(e) => setCompetitorFilter(e.target.value)}
            className="bg-[#09090B] border border-zinc-700 text-xs text-zinc-300 rounded-lg px-3 py-2 focus:outline-none focus:border-violet-500"
          >
            <option value="">All Competitors</option>
            {competitors.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#09090B] border border-zinc-700 text-xs text-zinc-300 rounded-lg px-3 py-2 focus:outline-none focus:border-violet-500"
          >
            <option value="">All Statuses</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILED">Failed</option>
          </select>

          <select
            value={methodFilter}
            onChange={(e) => setMethodFilter(e.target.value)}
            className="bg-[#09090B] border border-zinc-700 text-xs text-zinc-300 rounded-lg px-3 py-2 focus:outline-none focus:border-violet-500"
          >
            <option value="">All Methods</option>
            <option value="RSS">RSS</option>
            <option value="Sitemap">Sitemap</option>
            <option value="Direct Page">Direct Page</option>
          </select>

          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition"
            title="Refresh History"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* History Table */}
      {history.length === 0 ? (
        <div className="bg-[#18181B]/40 border border-[#27272A]/80 rounded-xl p-16 text-center text-zinc-500">
          <p className="text-sm font-semibold text-zinc-400">No monitoring check logs found</p>
          <p className="text-xs text-zinc-600 mt-1">
            Logs will appear here whenever a scheduled or manual check runs.
          </p>
        </div>
      ) : (
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#09090B]/60 text-zinc-400 font-semibold uppercase tracking-wider border-b border-[#27272A]">
                <tr>
                  <th className="py-3 px-4">Started At</th>
                  <th className="py-3 px-4">Competitor</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Articles Found</th>
                  <th className="py-3 px-4">New Articles</th>
                  <th className="py-3 px-4">Error / Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272A]/60">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-[#27272A]/30 transition">
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {new Date(item.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 font-semibold text-zinc-200">
                      {item.competitor_name || `Competitor #${item.competitor_id}`}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="py-3 px-4 font-mono text-zinc-300">
                      {item.response_time_ms} ms
                    </td>
                    <td className="py-3 px-4">
                      <StrategyBadge strategy={item.detection_method} />
                    </td>
                    <td className="py-3 px-4 font-mono text-zinc-300">
                      {item.articles_found}
                    </td>
                    <td className="py-3 px-4 font-mono">
                      {item.new_articles_found > 0 ? (
                        <span className="font-bold text-emerald-400">+{item.new_articles_found}</span>
                      ) : (
                        <span className="text-zinc-500">0</span>
                      )}
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      {item.error_message ? (
                        <span className="text-rose-400 font-mono text-[11px] truncate block" title={item.error_message}>
                          {item.error_message}
                        </span>
                      ) : (
                        <span className="text-zinc-500">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
