import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from backend.config import settings
from backend.services.article_extractor import ArticleExtractor
from backend.utils.url_helpers import normalize_url, make_absolute_url, is_same_domain
from backend.utils.date_helpers import calculate_detection_delay
from backend.utils.security import validate_target_url

logger = logging.getLogger(__name__)

EXCLUDE_PATH_KEYWORDS = {
    "tag", "tags", "category", "categories", "author", "authors", "page",
    "login", "signup", "register", "privacy", "terms", "contact", "about",
    "careers", "pricing", "search", "faq", "feed", "rss", "sitemap"
}

class PageMonitor:
    """
    Direct Blog/Article Page Monitor.
    Scrapes the blog listing page, detects new article links using semantic cues,
    filters duplicates, extracts full content, and calculates detection delay.
    """

    def __init__(self, extractor: Optional[ArticleExtractor] = None, timeout: int = 15):
        self.extractor = extractor or ArticleExtractor(timeout=timeout)
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def check_page(self, blog_url: str, existing_urls: Set[str]) -> Dict[str, Any]:
        valid_url = validate_target_url(blog_url)
        normalized_blog_url = normalize_url(valid_url)

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(normalized_blog_url, headers=self.headers)
            response.raise_for_status()
            html_content = response.text
            final_url = str(response.url)

        soup = BeautifulSoup(html_content, "html.parser")
        candidate_links = self._extract_article_links(soup, final_url)

        total_candidates = len(candidate_links)
        new_articles = []
        detection_timestamp = datetime.now(timezone.utc)

        for link in candidate_links:
            if link in existing_urls:
                continue

            article_data = None
            try:
                article_data = await self.extractor.fetch_and_extract(link)
            except Exception as e:
                logger.warning(f"Error extracting page {link}: {e}")

            if article_data:
                canonical = article_data.get("canonical_url") or link
                if canonical in existing_urls:
                    continue

                published_at = article_data.get("published_at")
                delay = calculate_detection_delay(published_at, detection_timestamp)

                new_articles.append({
                    "title": article_data.get("title") or "Untitled Article",
                    "content": article_data.get("content") or "",
                    "author": article_data.get("author"),
                    "published_at": published_at,
                    "detected_at": detection_timestamp,
                    "detection_delay_seconds": delay,
                    "detection_method": "Direct Page",
                    "canonical_url": canonical,
                    "source_url": link,
                    "meta_description": article_data.get("meta_description"),
                    "featured_image": article_data.get("featured_image"),
                    "categories": article_data.get("categories"),
                    "tags": article_data.get("tags"),
                    "relevant_links": article_data.get("relevant_links"),
                })
                existing_urls.add(canonical)
                existing_urls.add(link)

        return {
            "articles_found": total_candidates,
            "new_articles": new_articles,
        }

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Discovers article links using semantic cues, avoiding fragile single selectors.
        """
        links = []
        seen = set()

        # Remove header, footer, nav to isolate main listing
        clean_soup = BeautifulSoup(str(soup), "html.parser")
        for tag in clean_soup(["header", "footer", "nav", "aside"]):
            tag.decompose()

        # Priority 1: Semantic <article> elements
        articles = clean_soup.find_all("article")
        for art in articles:
            for a in art.find_all("a", href=True):
                full_url = make_absolute_url(base_url, a["href"])
                if self._is_valid_article_url(full_url, base_url) and full_url not in seen:
                    seen.add(full_url)
                    links.append(full_url)

        # Priority 2: Generic links inside main or card classes
        for container in clean_soup.find_all(class_=lambda c: c and any(w in c.lower() for w in ["post", "card", "blog", "article", "entry", "item", "grid"])):
            for a in container.find_all("a", href=True):
                full_url = make_absolute_url(base_url, a["href"])
                if self._is_valid_article_url(full_url, base_url) and full_url not in seen:
                    seen.add(full_url)
                    links.append(full_url)

        # Priority 3: Fallback all links on the page matching path patterns
        for a in clean_soup.find_all("a", href=True):
            full_url = make_absolute_url(base_url, a["href"])
            if self._is_valid_article_url(full_url, base_url) and full_url not in seen:
                seen.add(full_url)
                links.append(full_url)

        return links

    def _is_valid_article_url(self, url: str, base_url: str) -> bool:
        if not url:
            return False
        if not is_same_domain(url, base_url):
            return False
        if url == normalize_url(base_url):
            return False

        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            return False

        segments = [s.lower() for s in path.split("/")]
        
        # Avoid non-article sections
        if any(seg in EXCLUDE_PATH_KEYWORDS for seg in segments):
            return False

        # Avoid static file extensions
        if any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip", ".css", ".js"]):
            return False

        # Article URLs typically have at least 1 or 2 path segments
        return len(segments) >= 1
