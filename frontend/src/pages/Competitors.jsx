import React, { useState, useEffect } from "react";
import {
  Plus,
  RefreshCw,
  Search,
  ExternalLink,
  Trash2,
  CheckCircle2,
  XCircle,
  Loader2,
  Sparkles,
  Info,
} from "lucide-react";
import { api } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import { StrategyBadge } from "../components/StrategyBadge";

export function Competitors({ isAddModalOpen, setIsAddModalOpen }) {
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCompConfig, setSelectedCompConfig] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [actionInProgressId, setActionInProgressId] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    name: "",
    website_url: "",
    blog_url: "",
    rss_url: "",
    sitemap_url: "",
    monitoring_enabled: true,
  });

  const loadCompetitors = async () => {
    try {
      setLoading(true);
      const data = await api.getCompetitors();
      setCompetitors(data);
    } catch (err) {
      console.error("Error fetching competitors:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompetitors();
  }, []);

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsAnalyzing(true);
      await api.createCompetitor(formData);
      setIsAddModalOpen(false);
      setFormData({
        name: "",
        website_url: "",
        blog_url: "",
        rss_url: "",
        sitemap_url: "",
        monitoring_enabled: true,
      });
      await loadCompetitors();
    } catch (err) {
      alert(`Failed to add competitor: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTriggerCheck = async (id) => {
    try {
      setActionInProgressId(id);
      await api.triggerCheck(id);
      await loadCompetitors();
    } catch (err) {
      alert(`Check failed: ${err.message}`);
    } finally {
      setActionInProgressId(null);
    }
  };

  const handleReanalyze = async (id) => {
    try {
      setActionInProgressId(id);
      await api.reanalyzeCompetitor(id);
      await loadCompetitors();
    } catch (err) {
      alert(`Re-analysis failed: ${err.message}`);
    } finally {
      setActionInProgressId(null);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete '${name}' and all its stored articles and logs?`)) {
      return;
    }
    try {
      await api.deleteCompetitor(id);
      await loadCompetitors();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleViewConfig = async (id) => {
    try {
      const data = await api.getCompetitor(id);
      setSelectedCompConfig(data);
    } catch (err) {
      alert(`Could not fetch details: ${err.message}`);
    }
  };

  const filtered = competitors.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.website_url.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#18181B] p-4 rounded-xl border border-[#27272A]">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search competitors by name or URL..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#09090B] border border-zinc-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-violet-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadCompetitors}
            className="p-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition"
            title="Refresh List"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-violet-600/20 transition"
          >
            <Plus className="w-4 h-4" /> Add Competitor
          </button>
        </div>
      </div>

      {/* Competitors Grid / Cards */}
      {filtered.length === 0 ? (
        <div className="bg-[#18181B]/40 border border-[#27272A]/80 rounded-xl p-16 text-center text-zinc-500">
          <p className="text-sm font-semibold text-zinc-400">No competitors found</p>
          <p className="text-xs text-zinc-600 mt-1">
            Add a competitor website or click "Quick Demo Competitor" on the top navigation bar.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((comp) => (
            <div
              key={comp.id}
              className="bg-[#18181B] border border-[#27272A] rounded-xl p-5 hover:border-zinc-700 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-bold text-white tracking-tight">{comp.name}</h3>
                  <StatusBadge status={comp.monitoring_status} />
                </div>

                <a
                  href={comp.website_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 text-xs text-zinc-400 hover:text-[#8B5CF6] flex items-center gap-1 font-mono truncate"
                >
                  {comp.website_url} <ExternalLink className="w-3 h-3 shrink-0" />
                </a>

                <div className="mt-4 pt-3 border-t border-[#27272A] space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-500">Strategy</span>
                    <StrategyBadge strategy={comp.selected_strategy} />
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-500">Articles Found</span>
                    <span className="font-semibold text-white font-mono">{comp.articles_count ?? 0}</span>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-500">Last Checked</span>
                    <span className="text-zinc-400 font-mono">
                      {comp.last_checked_at
                        ? new Date(comp.last_checked_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                        : "Never"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-[#27272A] flex items-center justify-between gap-2">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleViewConfig(comp.id)}
                    className="p-1.5 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition text-xs font-semibold flex items-center gap-1"
                    title="View Auto-Discovered Signals"
                  >
                    <Info className="w-3.5 h-3.5" />
                    <span>Config</span>
                  </button>
                  <button
                    onClick={() => handleReanalyze(comp.id)}
                    disabled={actionInProgressId === comp.id}
                    className="p-1.5 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition text-xs font-semibold flex items-center gap-1"
                    title="Re-run Automatic Discovery"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    <span>Scan</span>
                  </button>
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handleTriggerCheck(comp.id)}
                    disabled={actionInProgressId === comp.id}
                    className="px-2.5 py-1.5 rounded-lg bg-violet-600/20 hover:bg-violet-600/30 text-violet-300 border border-violet-500/30 text-xs font-semibold flex items-center gap-1 transition disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3 h-3 ${actionInProgressId === comp.id ? "animate-spin" : ""}`} />
                    <span>Check Now</span>
                  </button>
                  <button
                    onClick={() => handleDelete(comp.id, comp.name)}
                    className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition"
                    title="Delete Competitor"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Competitor Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#09090B]/80 backdrop-blur-sm">
          <div className="bg-[#18181B] border border-[#27272A] rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#27272A]">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-[#8B5CF6]" /> Add Competitor Website
              </h2>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-zinc-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Competitor Name <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Tech, Stripe, Buffer"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1">
                  Website URL <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="https://example.com"
                  value={formData.website_url}
                  onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                  className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-violet-500"
                />
                <p className="text-[11px] text-zinc-500 mt-1">
                  The automatic analyzer will investigate feeds, sitemaps, and blog paths automatically.
                </p>
              </div>

              <div className="pt-2 border-t border-[#27272A]">
                <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider block mb-2">
                  Optional Explicit Overrides
                </span>

                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">Direct Blog URL (Optional)</label>
                    <input
                      type="text"
                      placeholder="https://example.com/blog"
                      value={formData.blog_url}
                      onChange={(e) => setFormData({ ...formData, blog_url: e.target.value })}
                      className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-violet-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">Direct RSS Feed URL (Optional)</label>
                    <input
                      type="text"
                      placeholder="https://example.com/feed.xml"
                      value={formData.rss_url}
                      onChange={(e) => setFormData({ ...formData, rss_url: e.target.value })}
                      className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-violet-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-zinc-400 mb-1">Direct Sitemap URL (Optional)</label>
                    <input
                      type="text"
                      placeholder="https://example.com/sitemap.xml"
                      value={formData.sitemap_url}
                      onChange={(e) => setFormData({ ...formData, sitemap_url: e.target.value })}
                      className="w-full bg-[#09090B] border border-zinc-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-violet-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="enabledCheck"
                  checked={formData.monitoring_enabled}
                  onChange={(e) => setFormData({ ...formData, monitoring_enabled: e.target.checked })}
                  className="rounded border-zinc-700 bg-zinc-900 text-violet-600 focus:ring-0"
                />
                <label htmlFor="enabledCheck" className="text-xs text-zinc-300 font-medium">
                  Enable continuous monitoring immediately
                </label>
              </div>

              <div className="pt-4 flex items-center justify-end gap-2 border-t border-[#27272A]">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 text-xs font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isAnalyzing}
                  className="px-5 py-2 rounded-lg bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-violet-600/20 disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Analyzing & Discovering...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5 text-violet-200" />
                      <span>Analyze & Add Competitor</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Discovered Configuration Modal */}
      {selectedCompConfig && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#09090B]/80 backdrop-blur-sm">
          <div className="bg-[#18181B] border border-[#27272A] rounded-2xl max-w-lg w-full p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#27272A]">
              <div>
                <h3 className="text-sm font-bold text-white">Discovered Configuration Signals</h3>
                <p className="text-xs text-zinc-400">{selectedCompConfig.competitor.name}</p>
              </div>
              <button
                onClick={() => setSelectedCompConfig(null)}
                className="text-zinc-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-[#09090B] border border-[#27272A] space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Selected Strategy:</span>
                  <StrategyBadge strategy={selectedCompConfig.competitor.selected_strategy} />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">RSS Available:</span>
                  <span className="font-mono text-white">
                    {selectedCompConfig.configuration?.rss_available ? "YES ✓" : "NO ✗"}
                  </span>
                </div>
                {selectedCompConfig.configuration?.rss_url && (
                  <div className="text-[11px] text-zinc-400 font-mono break-all">
                    URL: {selectedCompConfig.configuration.rss_url}
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">XML Sitemap Available:</span>
                  <span className="font-mono text-white">
                    {selectedCompConfig.configuration?.sitemap_available ? "YES ✓" : "NO ✗"}
                  </span>
                </div>
                {selectedCompConfig.configuration?.sitemap_url && (
                  <div className="text-[11px] text-zinc-400 font-mono break-all">
                    URL: {selectedCompConfig.configuration.sitemap_url}
                  </div>
                )}
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Sitemap Index:</span>
                  <span className="font-mono text-white">
                    {selectedCompConfig.configuration?.sitemap_index ? "Nested Index ✓" : "Standard URLset"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">JSON-LD Metadata:</span>
                  <span className="font-mono text-white">
                    {selectedCompConfig.configuration?.structured_metadata_available ? "Found ✓" : "None"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Publication Timestamp:</span>
                  <span className="font-mono text-white">
                    {selectedCompConfig.configuration?.publication_date_available ? "Extractable ✓" : "Unavailable"}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-5 flex justify-end">
              <button
                onClick={() => setSelectedCompConfig(null)}
                className="px-4 py-2 rounded-lg bg-[#27272A] text-zinc-300 text-xs font-semibold hover:bg-zinc-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
