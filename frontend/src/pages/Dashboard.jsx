import React, { useEffect, useState } from "react";
import {
  Users,
  Radio,
  FileText,
  Clock,
  Zap,
  TrendingDown,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Plus,
} from "lucide-react";
import { api } from "../services/api";
import { StatCard } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import { StrategyBadge } from "../components/StrategyBadge";
import { DelayBadge } from "../components/DelayBadge";

export function Dashboard({ onNavigate, onSelectArticle, onAddCompetitorClick }) {
  const [stats, setStats] = useState(null);
  const [competitors, setCompetitors] = useState([]);
  const [recentArticles, setRecentArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkingCompId, setCheckingCompId] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, compsData, articlesData] = await Promise.all([
        api.getDashboardStats(),
        api.getCompetitors(),
        api.getArticles({ limit: 8 }),
      ]);
      setStats(statsData);
      setCompetitors(compsData);
      setRecentArticles(articlesData);
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 20000); // Poll every 20s
    return () => clearInterval(interval);
  }, []);

  const handleQuickCheck = async (id, e) => {
    e.stopPropagation();
    try {
      setCheckingCompId(id);
      await api.triggerCheck(id);
      await loadData();
    } catch (err) {
      alert(`Check failed: ${err.message}`);
    } finally {
      setCheckingCompId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* 7 Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-3.5">
        <StatCard
          title="Total Competitors"
          value={stats?.total_competitors ?? 0}
          icon={Users}
          color="violet"
        />
        <StatCard
          title="Active Competitors"
          value={stats?.active_competitors ?? 0}
          icon={Radio}
          color="emerald"
        />
        <StatCard
          title="Articles Detected"
          value={stats?.articles_detected ?? 0}
          icon={FileText}
          color="indigo"
        />
        <StatCard
          title="Average Delay"
          value={stats?.average_detection_time || "—"}
          icon={Clock}
          color="amber"
          subtitle="From publish to detect"
        />
        <StatCard
          title="Fastest Delay"
          value={stats?.fastest_detection || "—"}
          icon={Zap}
          color="emerald"
          badge="Optimal"
        />
        <StatCard
          title="Slowest Delay"
          value={stats?.slowest_detection || "—"}
          icon={TrendingDown}
          color="amber"
        />
        <StatCard
          title="Failed Checks"
          value={stats?.failed_checks ?? 0}
          icon={AlertTriangle}
          color={stats?.failed_checks > 0 ? "rose" : "violet"}
          badge={`${stats?.success_rate_percent ?? 100}% Success`}
        />
      </div>

      {/* Monitoring Status Table */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#27272A] flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Competitor Monitoring Status</h2>
            <p className="text-xs text-zinc-400">Live health and polling telemetry across registered competitors</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onNavigate("competitors")}
              className="text-xs font-semibold text-[#8B5CF6] hover:text-violet-300 flex items-center gap-1 transition"
            >
              View All ({competitors.length}) <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onAddCompetitorClick}
              className="px-3 py-1.5 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition shadow-md shadow-violet-600/20"
            >
              <Plus className="w-3.5 h-3.5" /> Add Competitor
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#09090B]/60 text-zinc-400 font-semibold uppercase tracking-wider border-b border-[#27272A]">
              <tr>
                <th className="py-3 px-4">Competitor</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Strategy</th>
                <th className="py-3 px-4">Last Checked</th>
                <th className="py-3 px-4">Last Detection</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272A]/60">
              {competitors.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-10 text-center text-zinc-500">
                    No competitors currently registered. Click <strong>"Add Competitor"</strong> or <strong>"Quick Demo Competitor"</strong> to start.
                  </td>
                </tr>
              ) : (
                competitors.slice(0, 6).map((comp) => (
                  <tr key={comp.id} className="hover:bg-[#27272A]/40 transition">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-zinc-200">{comp.name}</div>
                      <a
                        href={comp.website_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-zinc-400 hover:text-[#8B5CF6] flex items-center gap-1 truncate max-w-xs font-mono"
                      >
                        {comp.website_url} <ExternalLink className="w-2.5 h-2.5 inline" />
                      </a>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={comp.monitoring_status} />
                    </td>
                    <td className="py-3 px-4">
                      <StrategyBadge strategy={comp.selected_strategy} />
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {comp.last_checked_at
                        ? new Date(comp.last_checked_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                        : "Never"}
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {comp.last_successful_detection_at
                        ? new Date(comp.last_successful_detection_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                        : "None"}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => handleQuickCheck(comp.id, e)}
                        disabled={checkingCompId === comp.id}
                        className="px-2.5 py-1 bg-[#27272A] hover:bg-zinc-700 text-zinc-200 rounded font-medium border border-zinc-700 transition disabled:opacity-50 inline-flex items-center gap-1"
                      >
                        <RefreshCw className={`w-3 h-3 ${checkingCompId === comp.id ? "animate-spin" : ""}`} />
                        <span>Check</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Latest Detected Articles */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-[#27272A] flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Latest Detected Articles</h2>
            <p className="text-xs text-zinc-400">Newly captured posts with exact detection delays and source attribution</p>
          </div>
          <button
            onClick={() => onNavigate("articles")}
            className="text-xs font-semibold text-[#8B5CF6] hover:text-violet-300 flex items-center gap-1 transition"
          >
            View All Articles <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#09090B]/60 text-zinc-400 font-semibold uppercase tracking-wider border-b border-[#27272A]">
              <tr>
                <th className="py-3 px-4">Article Title</th>
                <th className="py-3 px-4">Competitor</th>
                <th className="py-3 px-4">Method</th>
                <th className="py-3 px-4">Published At</th>
                <th className="py-3 px-4">Detected At</th>
                <th className="py-3 px-4">Detection Delay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#27272A]/60">
              {recentArticles.length === 0 ? (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-zinc-500">
                    No articles detected yet. Trigger a check or publish a test article in the Demo Controller!
                  </td>
                </tr>
              ) : (
                recentArticles.map((art) => (
                  <tr
                    key={art.id}
                    onClick={() => onSelectArticle(art.id)}
                    className="hover:bg-[#27272A]/40 transition cursor-pointer"
                  >
                    <td className="py-3 px-4">
                      <div className="font-semibold text-zinc-200 line-clamp-1 max-w-md hover:text-[#8B5CF6] transition">
                        {art.title}
                      </div>
                      <div className="text-[11px] text-zinc-500 font-mono truncate max-w-sm">
                        {art.canonical_url}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-medium text-zinc-300">
                      {art.competitor_name || "—"}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded font-mono font-semibold bg-[#27272A] text-zinc-300 border border-zinc-700">
                        {art.detection_method}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {art.published_at ? new Date(art.published_at).toLocaleString() : "Unavailable"}
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {new Date(art.detected_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <DelayBadge
                        delaySeconds={art.detection_delay_seconds}
                        delayFormatted={art.detection_delay_formatted}
                      />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
