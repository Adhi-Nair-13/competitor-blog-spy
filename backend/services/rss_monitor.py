import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
import httpx
import feedparser

from backend.config import settings
from backend.services.article_extractor import ArticleExtractor
from backend.utils.url_helpers import normalize_url
from backend.utils.date_helpers import parse_datetime, calculate_detection_delay
from backend.utils.security import validate_target_url

logger = logging.getLogger(__name__)

class RSSMonitor:
    """
    Monitors RSS/Atom feeds for newly published articles.
    Fetches the feed, checks for new entry URLs, extracts full article content,
    and calculates detection delay.
    """

    def __init__(self, extractor: Optional[ArticleExtractor] = None, timeout: int = 15):
        self.extractor = extractor or ArticleExtractor(timeout=timeout)
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        }

    async def check_feed(self, feed_url: str, existing_urls: Set[str]) -> Dict[str, Any]:
        valid_url = validate_target_url(feed_url)
        normalized_feed_url = normalize_url(valid_url)

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(normalized_feed_url, headers=self.headers)
            response.raise_for_status()
            feed_content = response.content

        parsed_feed = feedparser.parse(feed_content)
        if parsed_feed.bozo and not parsed_feed.entries:
            raise ValueError(f"Failed to parse RSS/Atom feed: {parsed_feed.bozo_exception}")

        total_entries = len(parsed_feed.entries)
        new_articles = []
        detection_timestamp = datetime.now(timezone.utc)

        for entry in parsed_feed.entries:
            raw_url = getattr(entry, "link", None)
            if not raw_url:
                continue
                
            entry_url = normalize_url(raw_url)
            if entry_url in existing_urls:
                continue

            # Fallback metadata from feed entry
            entry_title = getattr(entry, "title", "Untitled")
            entry_author = getattr(entry, "author", None)
            entry_summary = getattr(entry, "summary", None)
            
            entry_pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                entry_pub_date = parse_datetime(entry.published_parsed)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                entry_pub_date = parse_datetime(entry.updated_parsed)
            elif hasattr(entry, "published"):
                entry_pub_date = parse_datetime(entry.published)

            # Deep extraction of full article webpage
            article_data = None
            try:
                article_data = await self.extractor.fetch_and_extract(entry_url)
            except Exception as e:
                logger.warning(f"Could not extract full page for {entry_url}: {e}")

            if article_data:
                canonical_url = article_data.get("canonical_url") or entry_url
                if canonical_url in existing_urls:
                    continue

                published_at = article_data.get("published_at") or entry_pub_date
                title = article_data.get("title") or entry_title
                author = article_data.get("author") or entry_author
                content = article_data.get("content") or entry_summary
                
                delay = calculate_detection_delay(published_at, detection_timestamp)

                new_articles.append({
                    "title": title,
                    "content": content,
                    "author": author,
                    "published_at": published_at,
                    "detected_at": detection_timestamp,
                    "detection_delay_seconds": delay,
                    "detection_method": "RSS",
                    "canonical_url": canonical_url,
                    "source_url": entry_url,
                    "meta_description": article_data.get("meta_description") or entry_summary,
                    "featured_image": article_data.get("featured_image"),
                    "categories": article_data.get("categories"),
                    "tags": article_data.get("tags"),
                    "relevant_links": article_data.get("relevant_links"),
                })
                existing_urls.add(canonical_url)
                existing_urls.add(entry_url)
            else:
                # Use feed entry data as fallback
                delay = calculate_detection_delay(entry_pub_date, detection_timestamp)
                new_articles.append({
                    "title": entry_title,
                    "content": entry_summary or "",
                    "author": entry_author,
                    "published_at": entry_pub_date,
                    "detected_at": detection_timestamp,
                    "detection_delay_seconds": delay,
                    "detection_method": "RSS",
                    "canonical_url": entry_url,
                    "source_url": entry_url,
                    "meta_description": entry_summary,
                    "featured_image": None,
                    "categories": None,
                    "tags": None,
                    "relevant_links": None,
                })
                existing_urls.add(entry_url)

        return {
            "articles_found": total_entries,
            "new_articles": new_articles,
        }
