import pytest
from unittest.mock import AsyncMock, patch
from backend.services.rss_monitor import RSSMonitor
from backend.services.sitemap_monitor import SitemapMonitor

SAMPLE_RSS_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample Feed</title>
    <link>https://example.com/feed</link>
    <item>
      <title>Article One</title>
      <link>https://example.com/blog/article-1</link>
      <pubDate>Mon, 05 Oct 2026 12:00:00 GMT</pubDate>
      <description>Summary of article one.</description>
    </item>
  </channel>
</rss>
"""

SAMPLE_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/blog/article-sitemap-1</loc>
    <lastmod>2026-10-05T11:00:00Z</lastmod>
  </url>
</urlset>
"""

@pytest.mark.asyncio
async def test_rss_monitor_parses_entries():
    monitor = RSSMonitor()
    existing_urls = set()

    mock_article = {
        "title": "Article One",
        "content": "Full page content",
        "author": "Alice",
        "published_at": None,
        "canonical_url": "https://example.com/blog/article-1",
        "source_url": "https://example.com/blog/article-1",
    }

    with patch("httpx.AsyncClient.get") as mock_get, \
         patch.object(monitor.extractor, "fetch_and_extract", AsyncMock(return_value=mock_article)):
        mock_resp = AsyncMock()
        mock_resp.content = SAMPLE_RSS_XML
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        result = await monitor.check_feed("https://example.com/rss.xml", existing_urls)

    assert result["articles_found"] == 1
    assert len(result["new_articles"]) == 1
    art = result["new_articles"][0]
    assert art["title"] == "Article One"
    assert art["canonical_url"] == "https://example.com/blog/article-1"
    assert art["detection_method"] == "RSS"

@pytest.mark.asyncio
async def test_sitemap_monitor_parses_urlset():
    monitor = SitemapMonitor()
    existing_urls = set()

    mock_article = {
        "title": "Article Sitemap 1",
        "content": "Article from sitemap",
        "author": "Sitemap Author",
        "published_at": None,
        "canonical_url": "https://example.com/blog/article-sitemap-1",
        "source_url": "https://example.com/blog/article-sitemap-1",
    }

    with patch("httpx.AsyncClient.get") as mock_get, \
         patch.object(monitor.extractor, "fetch_and_extract", AsyncMock(return_value=mock_article)):
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_SITEMAP_XML
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        result = await monitor.check_sitemap("https://example.com/sitemap.xml", existing_urls)

    assert result["articles_found"] == 1
    assert len(result["new_articles"]) == 1
    art = result["new_articles"][0]
    assert art["canonical_url"] == "https://example.com/blog/article-sitemap-1"
    assert art["detection_method"] == "Sitemap"
