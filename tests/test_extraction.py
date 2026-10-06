from backend.services.article_extractor import ArticleExtractor

SAMPLE_HTML_WITH_JSON_LD = """
<!DOCTYPE html>
<html>
<head>
  <title>Default Page Title | Tech Blog</title>
  <link rel="canonical" href="https://example.com/blog/ai-future" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "The Rise of Autonomous AI Systems",
    "datePublished": "2026-10-04T09:30:00Z",
    "author": {
      "@type": "Person",
      "name": "Jane Doe"
    },
    "articleSection": "Artificial Intelligence",
    "keywords": "AI, Agents, Machine Learning"
  }
  </script>
</head>
<body>
  <article>
    <h1>The Rise of Autonomous AI Systems</h1>
    <p>This is the main body paragraph describing autonomous AI agent capabilities in full detail.</p>
    <a href="/related/agents">Related Post</a>
  </article>
</body>
</html>
"""

SAMPLE_HTML_NO_DATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Minimalist Article Without Date</title>
</head>
<body>
  <article>
    <h1>Undated Article Title</h1>
    <p class="author">By John Smith</p>
    <div class="content">Content without any publication timestamps present.</div>
  </article>
</body>
</html>
"""

def test_article_extractor_json_ld():
    extractor = ArticleExtractor()
    extracted = extractor.extract_from_html(SAMPLE_HTML_WITH_JSON_LD, base_url="https://example.com/blog/ai-future")

    assert extracted["title"] == "The Rise of Autonomous AI Systems"
    assert extracted["author"] == "Jane Doe"
    assert extracted["published_at"] is not None
    assert extracted["canonical_url"] == "https://example.com/blog/ai-future"
    assert "AI" in extracted["tags"]
    assert "Artificial Intelligence" in extracted["categories"]
    assert "autonomous AI agent capabilities" in extracted["content"]

def test_article_extractor_no_date_never_invents_date():
    extractor = ArticleExtractor()
    extracted = extractor.extract_from_html(SAMPLE_HTML_NO_DATE, base_url="https://example.com/posts/undated")

    assert extracted["title"] == "Undated Article Title"
    assert extracted["author"] == "John Smith"
    # Strict requirement: "Do not invent missing information. If publication date cannot be reliably determined, store it as null"
    assert extracted["published_at"] is None
