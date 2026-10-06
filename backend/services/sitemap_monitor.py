import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
import httpx
from bs4 import BeautifulSoup

from backend.config import settings
from backend.services.article_extractor import ArticleExtractor
from backend.utils.url_helpers import normalize_url
from backend.utils.date_helpers import parse_datetime, calculate_detection_delay
from backend.utils.security import validate_target_url

logger = logging.getLogger(__name__)

class SitemapMonitor:
    """
    Monitors XML Sitemaps and Sitemap Indexes.
    Recursively processes child sitemaps, extracts article URLs and lastmod dates,
    and identifies newly published articles.
    """

    def __init__(self, extractor: Optional[ArticleExtractor] = None, timeout: int = 15):
        self.extractor = extractor or ArticleExtractor(timeout=timeout)
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/xml, text/xml, */*",
        }

    async def check_sitemap(self, sitemap_url: str, existing_urls: Set[str]) -> Dict[str, Any]:
        valid_url = validate_target_url(sitemap_url)
        normalized_sitemap_url = normalize_url(valid_url)

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            entries = await self._parse_sitemap_recursive(client, normalized_sitemap_url, depth=0)

        total_entries = len(entries)
        new_articles = []
        detection_timestamp = datetime.now(timezone.utc)

        for item in entries:
            loc = normalize_url(item["loc"])
            lastmod = item.get("lastmod")

            if loc in existing_urls:
                continue

            path_segments = [p for p in loc.split("//")[-1].split("/") if p]
            if len(path_segments) <= 1:
                # Root home or root blog index (/blog, /news)
                continue
            if path_segments[-1].lower() in ["blog", "blogs", "articles", "news", "insights", "resources", "feed", "sitemap"]:
                continue

            article_data = None
            try:
                article_data = await self.extractor.fetch_and_extract(loc)
            except Exception as e:
                logger.warning(f"Error extracting article from sitemap URL {loc}: {e}")

            if article_data:
                canonical = article_data.get("canonical_url") or loc
                if canonical in existing_urls:
                    continue

                published_at = article_data.get("published_at") or lastmod
                delay = calculate_detection_delay(published_at, detection_timestamp)

                new_articles.append({
                    "title": article_data.get("title") or "Untitled Article",
                    "content": article_data.get("content") or "",
                    "author": article_data.get("author"),
                    "published_at": published_at,
                    "detected_at": detection_timestamp,
                    "detection_delay_seconds": delay,
                    "detection_method": "Sitemap",
                    "canonical_url": canonical,
                    "source_url": loc,
                    "meta_description": article_data.get("meta_description"),
                    "featured_image": article_data.get("featured_image"),
                    "categories": article_data.get("categories"),
                    "tags": article_data.get("tags"),
                    "relevant_links": article_data.get("relevant_links"),
                })
                existing_urls.add(canonical)
                existing_urls.add(loc)

        return {
            "articles_found": total_entries,
            "new_articles": new_articles,
        }

    async def _parse_sitemap_recursive(self, client: httpx.AsyncClient, url: str, depth: int = 0) -> List[Dict[str, Any]]:
        if depth > 2:  # Prevent infinite loops in nested sitemaps
            return []

        results = []
        try:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code != 200:
                return []
            content = resp.text
        except Exception as e:
            logger.warning(f"Failed to fetch sitemap {url}: {e}")
            return []

        try:
            soup = BeautifulSoup(content, "xml")
        except Exception:
            soup = BeautifulSoup(content, "html.parser")

        # 1. Sitemap Index handling (<sitemapindex>)
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            for s in sitemap_tags:
                loc_elem = s.find("loc")
                if loc_elem and loc_elem.get_text(strip=True):
                    child_url = loc_elem.get_text(strip=True)
                    # Filter for post/article/blog sitemaps when many are present
                    child_results = await self._parse_sitemap_recursive(client, child_url, depth=depth + 1)
                    results.extend(child_results)
            return results

        # 2. Standard URL set (<urlset>)
        url_tags = soup.find_all("url")
        for u in url_tags:
            loc_elem = u.find("loc")
            if not loc_elem or not loc_elem.get_text(strip=True):
                continue
            loc_val = loc_elem.get_text(strip=True)
            lastmod_val = None
            lastmod_elem = u.find("lastmod")
            if lastmod_elem and lastmod_elem.get_text(strip=True):
                lastmod_val = parse_datetime(lastmod_elem.get_text(strip=True))

            results.append({
                "loc": loc_val,
                "lastmod": lastmod_val,
            })

        return results
