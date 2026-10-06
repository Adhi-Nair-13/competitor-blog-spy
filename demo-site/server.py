import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Acme Corp Demo Blog")

# In-memory articles store initialized with 3 initial seed articles
ARTICLES_DB: List[Dict[str, Any]] = [
    {
        "id": 1,
        "slug": "future-of-ai-automation",
        "title": "The Future of AI Automation in Modern Enterprise",
        "author": "Dr. Sarah Chen",
        "published_at": "2026-10-01T10:00:00Z",
        "meta_description": "Exploring how generative models and autonomous agents are revolutionizing enterprise workflows.",
        "featured_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=60",
        "category": "Artificial Intelligence",
        "tags": ["AI", "Enterprise", "Automation"],
        "content": "<p>Autonomous agent workflows and real-time event-driven architectures are transforming corporate productivity across every sector.</p><p>Organizations integrating intelligent content pipelines report a 70% reduction in reporting latency, ensuring teams stay ahead of competitor initiatives.</p><p>As we advance into the late 2020s, automated monitoring systems will become the central nervous system for market intelligence.</p>",
    },
    {
        "id": 2,
        "slug": "scalable-web-scraping-best-practices",
        "title": "Architecting Resilient Real-Time Content Ingestion",
        "author": "Alex Rivera",
        "published_at": "2026-10-03T14:30:00Z",
        "meta_description": "Best practices for building robust scrapers that respect rate limits and gracefully handle network failures.",
        "featured_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=60",
        "category": "Engineering",
        "tags": ["Architecture", "Python", "Data Ingestion"],
        "content": "<p>Building resilient web scraping architectures requires multi-layered fallback strategies. Relying solely on single CSS selectors invites fragility.</p><p>By combining RSS/Atom feeds, XML sitemaps, and direct DOM diffing, ingestion systems achieve high fault-tolerance and minimal detection delay.</p>",
    },
    {
        "id": 3,
        "slug": "zero-latency-monitoring-insights",
        "title": "Zero-Latency Market Monitoring: Why Seconds Matter",
        "author": "Elena Rostova",
        "published_at": "2026-10-04T08:15:00Z",
        "meta_description": "How competitive intelligence platforms capture breaking changes before search engine indexation.",
        "featured_image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60",
        "category": "Competitive Intelligence",
        "tags": ["Analytics", "Strategy", "Real-Time"],
        "content": "<p>In fast-moving industries, being alerted to a competitor's product announcement or strategic blog post within 5 minutes allows your PR and product teams to react decisively.</p><p>This benchmark sets the gold standard for automated competitor monitoring products.</p>",
    },
]

class PublishRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = "Demo Publisher"
    content: Optional[str] = None
    category: Optional[str] = "Product Updates"

@app.get("/", response_class=HTMLResponse)
def homepage():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Acme Innovations - Official Company Site</title>
  <link rel="alternate" type="application/rss+xml" title="Acme Corp RSS Feed" href="/rss.xml" />
  <link rel="canonical" href="http://127.0.0.1:8001/" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans min-h-screen">
  <header class="bg-white border-b border-slate-200 py-4 px-8 flex justify-between items-center shadow-sm">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center text-white font-bold text-lg">A</div>
      <span class="text-xl font-bold text-slate-800">Acme Innovations</span>
    </div>
    <nav class="space-x-6 text-sm font-medium">
      <a href="/" class="text-indigo-600 hover:text-indigo-800">Home</a>
      <a href="/blog" class="text-slate-600 hover:text-slate-900">Blog</a>
      <a href="/control" class="px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100 font-semibold">⚡ Demo Control Panel</a>
    </nav>
  </header>
  <main class="max-w-4xl mx-auto px-4 py-16 text-center">
    <span class="px-3 py-1 bg-indigo-100 text-indigo-800 text-xs font-semibold rounded-full uppercase tracking-wider">Controlled Demo Target</span>
    <h1 class="text-4xl font-extrabold text-slate-900 mt-4 sm:text-5xl">Welcome to Acme Innovations</h1>
    <p class="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">This controlled website is used to test and verify the Competitor Blog Spy system. It contains an active RSS feed, XML sitemap, and rich JSON-LD structured articles.</p>
    <div class="mt-8 flex justify-center space-x-4">
      <a href="/blog" class="px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold shadow hover:bg-indigo-700 transition">Visit Our Blog</a>
      <a href="/control" class="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold shadow hover:bg-emerald-700 transition">⚡ Publish Test Article</a>
    </div>
  </main>
</body>
</html>"""

@app.get("/blog", response_class=HTMLResponse)
def blog_index():
    articles_html = ""
    for art in reversed(ARTICLES_DB):
        articles_html += f"""
        <article class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition mb-6">
          <div class="p-6">
            <div class="flex items-center text-xs text-slate-500 mb-2 space-x-2">
              <span class="bg-slate-100 px-2.5 py-0.5 rounded font-medium text-slate-700">{art['category']}</span>
              <span>•</span>
              <time datetime="{art['published_at']}">{art['published_at'][:10]}</time>
              <span>•</span>
              <span>By {art['author']}</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 mb-2 hover:text-indigo-600">
              <a href="/blog/{art['slug']}">{art['title']}</a>
            </h2>
            <p class="text-slate-600 text-sm mb-4">{art['meta_description']}</p>
            <a href="/blog/{art['slug']}" class="text-indigo-600 font-semibold text-sm hover:underline">Read Full Article →</a>
          </div>
        </article>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Acme Insights & Tech Blog</title>
  <link rel="alternate" type="application/rss+xml" title="Acme Blog Feed" href="/rss.xml" />
  <link rel="canonical" href="http://127.0.0.1:8001/blog" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans min-h-screen">
  <header class="bg-white border-b border-slate-200 py-4 px-8 flex justify-between items-center shadow-sm">
    <a href="/" class="text-xl font-bold text-slate-800">Acme Innovations Blog</a>
    <div class="space-x-4">
      <a href="/rss.xml" class="text-orange-500 text-sm font-semibold hover:underline">RSS Feed</a>
      <a href="/sitemap.xml" class="text-blue-500 text-sm font-semibold hover:underline">Sitemap</a>
      <a href="/control" class="px-3 py-1 bg-emerald-600 text-white rounded text-sm font-semibold hover:bg-emerald-700">⚡ Publish New Post</a>
    </div>
  </header>
  <main class="max-w-4xl mx-auto px-4 py-10">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-slate-900">Latest Articles & Insights</h1>
      <p class="text-slate-600 text-sm mt-1">Dispatches from our engineering and product teams.</p>
    </div>
    <div class="space-y-4">
      {articles_html}
    </div>
  </main>
</body>
</html>"""

@app.get("/blog/{slug}", response_class=HTMLResponse)
def article_detail(slug: str):
    article = next((a for a in ARTICLES_DB if a["slug"] == slug), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article_url = f"http://127.0.0.1:8001/blog/{article['slug']}"
    
    # JSON-LD Structured Data
    json_ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article["title"],
        "description": article["meta_description"],
        "datePublished": article["published_at"],
        "dateModified": article["published_at"],
        "url": article_url,
        "author": {
            "@type": "Person",
            "name": article["author"]
        },
        "publisher": {
            "@type": "Organization",
            "name": "Acme Innovations"
        },
        "image": article.get("featured_image"),
        "articleSection": article["category"],
        "keywords": ", ".join(article.get("tags", []))
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{article['title']} | Acme Innovations</title>
  <meta name="description" content="{article['meta_description']}" />
  <meta name="author" content="{article['author']}" />
  <meta property="og:title" content="{article['title']}" />
  <meta property="og:description" content="{article['meta_description']}" />
  <meta property="og:url" content="{article_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="{article.get('featured_image', '')}" />
  <meta property="article:published_time" content="{article['published_at']}" />
  <meta property="article:author" content="{article['author']}" />
  <link rel="canonical" href="{article_url}" />
  <link rel="alternate" type="application/rss+xml" title="Acme RSS Feed" href="/rss.xml" />
  <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans min-h-screen">
  <header class="bg-white border-b border-slate-200 py-4 px-8 flex justify-between items-center shadow-sm">
    <a href="/blog" class="text-lg font-bold text-slate-800">← Back to Acme Blog</a>
    <a href="/control" class="px-3 py-1 bg-emerald-600 text-white rounded text-sm font-semibold hover:bg-emerald-700">⚡ Demo Control</a>
  </header>
  <main class="max-w-3xl mx-auto px-4 py-12">
    <article class="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
      <div class="flex items-center text-xs text-slate-500 mb-4 space-x-2">
        <span class="bg-indigo-50 text-indigo-700 px-2.5 py-0.5 rounded font-medium">{article['category']}</span>
        <span>•</span>
        <time datetime="{article['published_at']}">{article['published_at']}</time>
      </div>
      <h1 class="text-3xl font-extrabold text-slate-900 mb-3">{article['title']}</h1>
      <div class="flex items-center space-x-2 text-sm text-slate-600 mb-6 pb-6 border-b border-slate-100">
        <span>By <strong class="text-slate-800 author-name">{article['author']}</strong></span>
      </div>
      {f'<img src="{article["featured_image"]}" alt="{article["title"]}" class="w-full h-64 object-cover rounded-xl mb-6" />' if article.get("featured_image") else ''}
      <div class="prose max-w-none text-slate-700 leading-relaxed space-y-4 article-body">
        {article['content']}
      </div>
      <div class="mt-8 pt-6 border-t border-slate-100 flex flex-wrap gap-2">
        {''.join(f'<span class="bg-slate-100 text-slate-600 text-xs px-2.5 py-1 rounded">#{tag}</span>' for tag in article.get("tags", []))}
      </div>
    </article>
  </main>
</body>
</html>"""

@app.get("/rss.xml")
def rss_feed():
    items_xml = ""
    for art in reversed(ARTICLES_DB):
        pub_dt = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        rfc_date = format_datetime(pub_dt)
        items_xml += f"""
    <item>
      <title><![CDATA[{art['title']}]]></title>
      <link>http://127.0.0.1:8001/blog/{art['slug']}</link>
      <guid isPermaLink="true">http://127.0.0.1:8001/blog/{art['slug']}</guid>
      <pubDate>{rfc_date}</pubDate>
      <author>{art['author']}</author>
      <description><![CDATA[{art['meta_description']}]]></description>
      <category>{art['category']}</category>
    </item>"""

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Acme Innovations Official Feed</title>
    <link>http://127.0.0.1:8001/blog</link>
    <description>Real-time corporate insights and technology announcements.</description>
    <language>en-us</language>
    <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
    <atom:link href="http://127.0.0.1:8001/rss.xml" rel="self" type="application/rss+xml" />
    {items_xml}
  </channel>
</rss>"""
    return Response(content=feed_xml, media_type="application/xml")

@app.get("/sitemap.xml")
def sitemap_xml():
    urls_xml = """
    <url>
      <loc>http://127.0.0.1:8001/</loc>
      <changefreq>daily</changefreq>
      <priority>1.0</priority>
    </url>
    <url>
      <loc>http://127.0.0.1:8001/blog</loc>
      <changefreq>hourly</changefreq>
      <priority>0.9</priority>
    </url>"""

    for art in ARTICLES_DB:
        urls_xml += f"""
    <url>
      <loc>http://127.0.0.1:8001/blog/{art['slug']}</loc>
      <lastmod>{art['published_at']}</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.8</priority>
    </url>"""

    sitemap_doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>"""
    return Response(content=sitemap_doc, media_type="application/xml")

@app.post("/api/publish")
def publish_article(payload: Optional[PublishRequest] = None):
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    now_str = now.strftime("%H:%M:%S")
    
    new_id = len(ARTICLES_DB) + 1
    custom_title = payload.title if payload and payload.title else f"Breaking Breakthrough: Project Orion Launch #{new_id} ({now_str})"
    slug = f"project-orion-launch-{new_id}-{int(now.timestamp())}"
    
    new_article = {
        "id": new_id,
        "slug": slug,
        "title": custom_title,
        "author": payload.author if payload and payload.author else "Acme Product Team",
        "published_at": now_iso,
        "meta_description": f"Live test announcement published at {now_str} to demonstrate real-time competitor detection delay.",
        "featured_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop&q=60",
        "category": payload.category if payload and payload.category else "Product Updates",
        "tags": ["Demo", "BreakingNews", "LiveDetection"],
        "content": f"<p>This article was freshly published at <strong>{now_iso}</strong> specifically to test immediate detection delay.</p><p>When the Competitor Blog Spy system checks the Acme demo site, it will extract this title, calculate the exact detection delay in seconds, and create a real-time notification.</p>",
    }

    ARTICLES_DB.append(new_article)
    return {
        "status": "published",
        "article": new_article,
        "published_at": now_iso,
        "total_articles": len(ARTICLES_DB)
    }

@app.get("/control", response_class=HTMLResponse)
def control_panel():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Demo Site Publisher - Test Control Panel</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex items-center justify-center p-6">
  <div class="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-lg w-full shadow-2xl">
    <div class="flex items-center space-x-3 mb-6">
      <div class="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xl">⚡</div>
      <div>
        <h1 class="text-xl font-bold text-white">Live Test Article Publisher</h1>
        <p class="text-slate-400 text-xs">Simulate instant competitor blog publication</p>
      </div>
    </div>

    <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800 text-sm mb-6 space-y-2">
      <p class="text-slate-300"><strong>How to test:</strong></p>
      <ol class="list-decimal list-inside text-xs text-slate-400 space-y-1">
        <li>Click <strong>Publish New Test Article</strong> below.</li>
        <li>Switch to the Competitor Blog Spy Dashboard.</li>
        <li>Trigger a check or wait for continuous monitoring.</li>
        <li>Observe the exact detection delay (e.g. <em>14 seconds</em>) and new notification!</li>
      </ol>
    </div>

    <form id="publishForm" class="space-y-4">
      <div>
        <label class="block text-xs font-semibold text-slate-300 mb-1">Article Title (Optional)</label>
        <input type="text" id="titleInput" placeholder="Auto-generated with current timestamp..." class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500" />
      </div>

      <button type="submit" id="publishBtn" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition flex items-center justify-center space-x-2">
        <span>🚀 Publish Test Article Now</span>
      </button>
    </form>

    <div id="resultBox" class="mt-6 hidden bg-emerald-950/50 border border-emerald-800/80 p-4 rounded-xl text-xs text-emerald-300">
      <p class="font-bold text-emerald-200">✅ Article Successfully Published!</p>
      <p id="resTitle" class="mt-1 font-semibold"></p>
      <p id="resTime" class="text-slate-400 mt-1"></p>
      <p class="mt-2 text-xs text-emerald-400">Head over to the Dashboard to trigger detection and see the delay badge!</p>
    </div>
  </div>

  <script>
    document.getElementById('publishForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('publishBtn');
      const title = document.getElementById('titleInput').value;
      btn.disabled = true;
      btn.textContent = 'Publishing...';

      try {
        const resp = await fetch('/api/publish', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: title || undefined })
        });
        const data = await resp.json();
        document.getElementById('resultBox').classList.remove('hidden');
        document.getElementById('resTitle').textContent = data.article.title;
        document.getElementById('resTime').textContent = 'Published At: ' + data.published_at;
      } catch (err) {
        alert('Failed to publish article: ' + err);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🚀 Publish Another Article</span>';
      }
    });
  </script>
</body>
</html>"""

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)
