import React, { useState } from "react";
import {
  Radio,
  ExternalLink,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  Clock,
  ArrowRight,
  Flame,
} from "lucide-react";
import { api } from "../services/api";

export function DemoControl({ onNavigate, onSelectArticle }) {
  const [publishing, setPublishing] = useState(false);
  const [publishedArticle, setPublishedArticle] = useState(null);
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState(null);

  const handlePublish = async () => {
    try {
      setPublishing(true);
      setCheckResult(null);
      const res = await api.publishTestArticle();
      if (res.error) {
        alert(res.error);
      } else {
        setPublishedArticle(res);
      }
    } catch (err) {
      alert(`Publishing failed: ${err.message}`);
    } finally {
      setPublishing(false);
    }
  };

  const handleCheckNow = async () => {
    try {
      setChecking(true);
      await api.runAllChecks();
      await new Promise((r) => setTimeout(r, 1500));
      const recent = await api.getArticles({ limit: 1 });
      if (recent && recent.length > 0) {
        setCheckResult(recent[0]);
      }
    } catch (err) {
      alert(`Check failed: ${err.message}`);
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Overview Banner */}
      <div className="bg-gradient-to-r from-violet-950/40 via-indigo-950/30 to-[#18181B] border border-violet-500/30 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-600/30 text-[#8B5CF6] border border-violet-500/40 flex items-center justify-center">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <span className="px-2.5 py-0.5 rounded font-mono text-[10px] font-bold bg-violet-500/20 text-violet-300 uppercase tracking-wider">
              Evaluation & Live Demonstration Mode
            </span>
            <h2 className="text-xl font-bold text-white mt-1">Interactive Controlled Demo Controller</h2>
          </div>
        </div>

        <p className="mt-3 text-xs text-zinc-300 leading-relaxed">
          The controlled demo website runs independently at{" "}
          <a
            href="http://127.0.0.1:8001"
            target="_blank"
            rel="noreferrer"
            className="text-[#8B5CF6] font-mono font-semibold underline"
          >
            http://127.0.0.1:8001
          </a>
          . Use the steps below to publish a brand new article and watch the monitoring engine discover it, calculate exact detection delay down to the second, and trigger a dashboard notification.
        </p>

        {/* Quick Links to Controlled Site */}
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <a
            href="http://127.0.0.1:8001"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-[#27272A]/80 hover:bg-[#27272A] text-zinc-300 flex items-center gap-1.5 transition font-medium border border-zinc-700"
          >
            Demo Homepage <ExternalLink className="w-3 h-3 text-zinc-500" />
          </a>
          <a
            href="http://127.0.0.1:8001/blog"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-[#27272A]/80 hover:bg-[#27272A] text-zinc-300 flex items-center gap-1.5 transition font-medium border border-zinc-700"
          >
            Demo Blog Index <ExternalLink className="w-3 h-3 text-zinc-500" />
          </a>
          <a
            href="http://127.0.0.1:8001/rss.xml"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-[#27272A]/80 hover:bg-[#27272A] text-amber-400 flex items-center gap-1.5 transition font-medium border border-zinc-700"
          >
            RSS Feed (XML) <ExternalLink className="w-3 h-3 text-zinc-500" />
          </a>
          <a
            href="http://127.0.0.1:8001/sitemap.xml"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-[#27272A]/80 hover:bg-[#27272A] text-indigo-400 flex items-center gap-1.5 transition font-medium border border-zinc-700"
          >
            Sitemap.xml <ExternalLink className="w-3 h-3 text-zinc-500" />
          </a>
        </div>
      </div>

      {/* Step by Step Demonstration Workflow */}
      <div className="space-y-4">
        {/* Step 1: Publish */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-violet-600/20 text-[#8B5CF6] flex items-center justify-center font-bold text-xs">
                1
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Publish New Article to Controlled Demo Site</h3>
                <p className="text-xs text-zinc-400">
                  Injects a new blog post into the demo blog, updating its RSS feed, Sitemap, and HTML DOM.
                </p>
              </div>
            </div>

            <button
              onClick={handlePublish}
              disabled={publishing}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-emerald-600/20 disabled:opacity-50"
            >
              <Flame className="w-4 h-4 text-emerald-200" />
              <span>{publishing ? "Publishing..." : "⚡ Publish Test Article Now"}</span>
            </button>
          </div>

          {publishedArticle && (
            <div className="mt-4 p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs space-y-1 animate-fadeIn">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>Article Successfully Published on Demo Website!</span>
              </div>
              <p className="text-zinc-200 font-semibold">{publishedArticle.article.title}</p>
              <p className="text-zinc-400 font-mono text-[11px]">
                Publication Timestamp: {publishedArticle.published_at}
              </p>
            </div>
          )}
        </div>

        {/* Step 2: Trigger Detection Check */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full bg-violet-600/20 text-[#8B5CF6] flex items-center justify-center font-bold text-xs">
                2
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Run Detection Engine</h3>
                <p className="text-xs text-zinc-400">
                  Inspects the demo website feeds and pages, detects the new article, and calculates detection delay.
                </p>
              </div>
            </div>

            <button
              onClick={handleCheckNow}
              disabled={checking}
              className="px-4 py-2 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-violet-600/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${checking ? "animate-spin" : ""}`} />
              <span>{checking ? "Scanning Target..." : "Run Detection Check"}</span>
            </button>
          </div>

          {checkResult && (
            <div className="mt-4 p-4 rounded-xl bg-[#09090B] border border-violet-500/40 text-xs space-y-2 animate-fadeIn">
              <div className="flex items-center justify-between">
                <span className="text-[#8B5CF6] font-bold flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-[#8B5CF6]" />
                  Target Discovered & Ingested!
                </span>
                <span className="px-2 py-0.5 rounded font-mono font-bold bg-[#27272A] text-zinc-300 border border-zinc-700">
                  Method: {checkResult.detection_method}
                </span>
              </div>

              <p className="text-white font-bold text-sm">{checkResult.title}</p>

              <div className="flex flex-wrap items-center gap-3 pt-2 text-zinc-300">
                <span className="flex items-center gap-1 font-mono">
                  <Clock className="w-3.5 h-3.5 text-zinc-500" />
                  Detection Delay: <strong className="text-emerald-400">{checkResult.detection_delay_formatted}</strong>
                </span>

                <button
                  onClick={() => onSelectArticle(checkResult.id)}
                  className="text-[#8B5CF6] hover:text-violet-300 font-semibold underline flex items-center gap-1"
                >
                  View Article Reader <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
