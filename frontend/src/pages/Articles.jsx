import React, { useState, useEffect } from "react";
import { Search, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { DelayBadge } from "../components/DelayBadge";
import { ArticleDetailModal } from "./ArticleDetailModal";

export function Articles({ initialArticleId = null }) {
  const [articles, setArticles] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticleId, setSelectedArticleId] = useState(initialArticleId);

  // Filters
  const [search, setSearch] = useState("");
  const [competitorFilter, setCompetitorFilter] = useState("");
  const [methodFilter, setMethodFilter] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [articlesData, compsData] = await Promise.all([
        api.getArticles({
          competitor_id: competitorFilter || undefined,
          detection_method: methodFilter || undefined,
          search: search || undefined,
          limit: 100,
        }),
        api.getCompetitors(),
      ]);
      setArticles(articlesData);
      setCompetitors(compsData);
    } catch (err) {
      console.error("Failed to load articles:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [competitorFilter, methodFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-6">
      {/* Controls & Filter Bar */}
      <div className="bg-[#18181B] p-4 rounded-xl border border-[#27272A] flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search articles by title, author, or keywords..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#09090B] border border-zinc-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-violet-500"
          />
        </form>

        {/* Filters */}
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
            value={methodFilter}
            onChange={(e) => setMethodFilter(e.target.value)}
            className="bg-[#09090B] border border-zinc-700 text-xs text-zinc-300 rounded-lg px-3 py-2 focus:outline-none focus:border-violet-500"
          >
            <option value="">All Detection Methods</option>
            <option value="RSS">RSS Feed</option>
            <option value="Sitemap">XML Sitemap</option>
            <option value="Direct Page">Direct Page DOM</option>
          </select>

          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-300 transition"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Articles Listing */}
      {articles.length === 0 ? (
        <div className="bg-[#18181B]/40 border border-[#27272A]/80 rounded-xl p-16 text-center text-zinc-500">
          <p className="text-sm font-semibold text-zinc-400">No articles found</p>
          <p className="text-xs text-zinc-600 mt-1">
            Try adjusting your search criteria or trigger a check on your competitors.
          </p>
        </div>
      ) : (
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#09090B]/60 text-zinc-400 font-semibold uppercase tracking-wider border-b border-[#27272A]">
                <tr>
                  <th className="py-3 px-4">Article</th>
                  <th className="py-3 px-4">Competitor</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Published</th>
                  <th className="py-3 px-4">Detected</th>
                  <th className="py-3 px-4">Detection Delay</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272A]/60">
                {articles.map((art) => (
                  <tr
                    key={art.id}
                    onClick={() => setSelectedArticleId(art.id)}
                    className="hover:bg-[#27272A]/40 transition cursor-pointer"
                  >
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-zinc-200 line-clamp-1 max-w-lg hover:text-[#8B5CF6] transition text-sm">
                        {art.title}
                      </div>
                      <div className="text-[11px] text-zinc-500 font-mono truncate max-w-md mt-0.5">
                        {art.canonical_url}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-zinc-300">
                      {art.competitor_name || "—"}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded font-mono font-semibold bg-[#27272A] text-zinc-300 border border-zinc-700">
                        {art.detection_method}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400 font-mono">
                      {art.published_at ? new Date(art.published_at).toLocaleString() : "Unavailable"}
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400 font-mono">
                      {new Date(art.detected_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <DelayBadge
                        delaySeconds={art.detection_delay_seconds}
                        delayFormatted={art.detection_delay_formatted}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Reader Modal */}
      {selectedArticleId && (
        <ArticleDetailModal
          articleId={selectedArticleId}
          onClose={() => setSelectedArticleId(null)}
        />
      )}
    </div>
  );
}
