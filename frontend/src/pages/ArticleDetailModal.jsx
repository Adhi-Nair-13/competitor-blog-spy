import React, { useEffect, useState } from "react";
import { X, Calendar, Clock, User } from "lucide-react";
import { api } from "../services/api";
import { DelayBadge } from "../components/DelayBadge";

export function ArticleDetailModal({ articleId, onClose }) {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!articleId) return;
    const fetchArticle = async () => {
      try {
        setLoading(true);
        const data = await api.getArticle(articleId);
        setArticle(data);
      } catch (err) {
        console.error("Failed to load article detail:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchArticle();
  }, [articleId]);

  if (!articleId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#09090B]/80 backdrop-blur-sm overflow-y-auto">
      <div className="bg-[#18181B] border border-[#27272A] rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden my-auto">
        {/* Header */}
        <div className="p-5 border-b border-[#27272A] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded bg-violet-500/10 text-[#8B5CF6] border border-violet-500/20 text-xs font-semibold">
              {article?.competitor_name || "Competitor Article"}
            </span>
            <span className="text-xs text-zinc-500">•</span>
            <span className="text-xs text-zinc-400 font-mono">
              Method: <strong className="text-zinc-200">{article?.detection_method}</strong>
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-[#27272A] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-20 text-center text-zinc-500 text-sm">
              Loading extracted article...
            </div>
          ) : article ? (
            <>
              {/* Title & Metadata */}
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight">{article.title}</h1>

                <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-zinc-400 border-b border-[#27272A] pb-4">
                  {article.author && (
                    <div className="flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-zinc-500" />
                      <span>{article.author}</span>
                    </div>
                  )}

                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-zinc-500" />
                    <span>
                      Published: {article.published_at ? new Date(article.published_at).toLocaleString() : "Unavailable"}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-zinc-500" />
                    <span>Detected: {new Date(article.detected_at).toLocaleString()}</span>
                  </div>

                  <DelayBadge
                    delaySeconds={article.detection_delay_seconds}
                    delayFormatted={article.detection_delay_formatted}
                  />
                </div>
              </div>

              {/* Featured Image */}
              {article.featured_image && (
                <div className="rounded-xl overflow-hidden border border-[#27272A] bg-[#09090B]">
                  <img
                    src={article.featured_image}
                    alt={article.title}
                    className="w-full h-64 object-cover"
                    onError={(e) => (e.target.style.display = "none")}
                  />
                </div>
              )}

              {/* Meta Description */}
              {article.meta_description && (
                <div className="bg-[#09090B]/60 p-4 rounded-xl border border-[#27272A] text-xs text-zinc-300 italic">
                  "{article.meta_description}"
                </div>
              )}

              {/* Extracted Body */}
              <div className="text-zinc-200 text-sm leading-relaxed space-y-3 prose-invert max-w-none">
                {article.content ? (
                  <div dangerouslySetInnerHTML={{ __html: article.content }} />
                ) : (
                  <p className="text-zinc-500 italic">No body text available.</p>
                )}
              </div>

              {/* Tags & Categories */}
              {(article.categories || article.tags) && (
                <div className="pt-4 border-t border-[#27272A] flex flex-wrap gap-2 text-xs">
                  {article.categories && (
                    <span className="px-2.5 py-1 rounded bg-[#27272A] text-violet-300 border border-zinc-700">
                      Category: {article.categories}
                    </span>
                  )}
                  {article.tags &&
                    article.tags.split(",").map((t, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-[#27272A]/60 text-zinc-400 border border-[#27272A] text-[11px]"
                      >
                        #{t.trim()}
                      </span>
                    ))}
                </div>
              )}

              {/* Canonical and Source Links */}
              <div className="pt-4 border-t border-[#27272A] text-xs text-zinc-400 space-y-1 font-mono">
                <div className="flex items-center gap-2">
                  <span className="text-zinc-500">Canonical:</span>
                  <a
                    href={article.canonical_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[#8B5CF6] hover:underline truncate"
                  >
                    {article.canonical_url}
                  </a>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-zinc-500">Source:</span>
                  <a
                    href={article.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-zinc-300 hover:underline truncate"
                  >
                    {article.source_url}
                  </a>
                </div>
              </div>
            </>
          ) : (
            <div className="py-20 text-center text-rose-400 text-sm">
              Article not found.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#27272A] bg-[#09090B]/40 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-[#27272A] hover:bg-zinc-700 text-zinc-200 text-xs font-semibold transition"
          >
            Close Reader
          </button>
        </div>
      </div>
    </div>
  );
}
