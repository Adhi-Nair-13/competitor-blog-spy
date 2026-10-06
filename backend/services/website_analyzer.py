import logging
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

from backend.config import settings
from backend.utils.url_helpers import normalize_url, make_absolute_url, is_same_domain
from backend.utils.security import validate_target_url

logger = logging.getLogger(__name__)

COMMON_FEED_PATHS = [
    "/feed",
    "/rss",
    "/rss.xml",
    "/feed.xml",
    "/atom.xml",
    "/index.xml",
    "/blog/feed",
    "/blog/rss.xml",
    "/blog/atom.xml",
    "/news/feed",
]

COMMON_BLOG_KEYWORDS = ["blog", "blogs", "articles", "news", "insights", "resources", "posts", "stories"]

class WebsiteAnalyzer:
    """
    Automatically investigates a competitor website.
    Discovers:
    - RSS and Atom feeds
    - Sitemaps and Sitemap indexes
    - Blog/article root pages
    - Metadata and article signals
    And determines the best monitoring strategy.
    """

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def analyze_website(self, root_url: str, user_blog_url: Optional[str] = None, user_rss_url: Optional[str] = None, user_sitemap_url: Optional[str] = None) -> Dict[str, Any]:
        valid_root = validate_target_url(root_url)
        normalized_root = normalize_url(valid_root)

        rss_available = False
        atom_available = False
        discovered_rss_url = normalize_url(user_rss_url) if user_rss_url else None
        
        sitemap_available = False
        sitemap_is_index = False
        discovered_sitemap_url = normalize_url(user_sitemap_url) if user_sitemap_url else None
        
        discovered_blog_url = normalize_url(user_blog_url) if user_blog_url else None
        article_pattern = None
        publication_date_available = False
        structured_metadata_available = False
        canonical_url_available = False

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            # 1. Fetch homepage
            homepage_html = ""
            final_root_url = normalized_root
            try:
                resp = await client.get(normalized_root, headers=self.headers)
                if resp.status_code < 400:
                    homepage_html = resp.text
                    final_root_url = str(resp.url)
            except Exception as e:
                logger.warning(f"Error fetching root homepage {normalized_root}: {e}")

            soup = BeautifulSoup(homepage_html, "html.parser") if homepage_html else None

            # 2. Check for RSS/Atom in HTML <head>
            if soup and not discovered_rss_url:
                feed_links = soup.find_all("link", rel=lambda val: val and "alternate" in val.lower())
                for link in feed_links:
                    feed_type = (link.get("type") or "").lower()
                    href = link.get("href")
                    if not href:
                        continue
                    if "rss" in feed_type or "xml" in feed_type:
                        discovered_rss_url = make_absolute_url(final_root_url, href)
                        rss_available = True
                        break
                    elif "atom" in feed_type:
                        discovered_rss_url = make_absolute_url(final_root_url, href)
                        atom_available = True
                        break

            # 3. Check common RSS/Atom paths if not yet discovered
            if not discovered_rss_url:
                for path in COMMON_FEED_PATHS:
                    candidate = make_absolute_url(final_root_url, path)
                    try:
                        r = await client.head(candidate, headers=self.headers)
                        if r.status_code == 200:
                            content_type = r.headers.get("content-type", "").lower()
                            if any(t in content_type for t in ["xml", "rss", "atom"]):
                                discovered_rss_url = candidate
                                rss_available = True
                                if "atom" in content_type:
                                    atom_available = True
                                break
                            else:
                                # Test with GET
                                r_get = await client.get(candidate, headers=self.headers)
                                if "<rss" in r_get.text.lower() or "<feed" in r_get.text.lower():
                                    discovered_rss_url = candidate
                                    rss_available = True
                                    if "<feed" in r_get.text.lower():
                                        atom_available = True
                                    break
                    except Exception:
                        continue
            else:
                rss_available = True

            # 4. Check Sitemap via robots.txt and standard /sitemap.xml
            if not discovered_sitemap_url:
                # Check robots.txt
                robots_url = make_absolute_url(final_root_url, "/robots.txt")
                try:
                    robots_resp = await client.get(robots_url, headers=self.headers)
                    if robots_resp.status_code == 200:
                        for line in robots_resp.text.splitlines():
                            line_strip = line.strip()
                            if line_strip.lower().startswith("sitemap:"):
                                parts = line_strip.split(":", 1)
                                if len(parts) > 1:
                                    candidate = parts[1].strip()
                                    if candidate.startswith("http"):
                                        discovered_sitemap_url = normalize_url(candidate)
                                        sitemap_available = True
                                        break
                except Exception:
                    pass

            if not discovered_sitemap_url:
                # Check /sitemap.xml
                sitemap_candidate = make_absolute_url(final_root_url, "/sitemap.xml")
                try:
                    s_resp = await client.get(sitemap_candidate, headers=self.headers)
                    if s_resp.status_code == 200 and ("<urlset" in s_resp.text.lower() or "<sitemapindex" in s_resp.text.lower()):
                        discovered_sitemap_url = sitemap_candidate
                        sitemap_available = True
                        if "<sitemapindex" in s_resp.text.lower():
                            sitemap_is_index = True
                except Exception:
                    pass
            elif discovered_sitemap_url:
                sitemap_available = True
                try:
                    s_resp = await client.get(discovered_sitemap_url, headers=self.headers)
                    if s_resp.status_code == 200 and "<sitemapindex" in s_resp.text.lower():
                        sitemap_is_index = True
                except Exception:
                    pass

            # 5. Discover Blog URL if not provided
            if not discovered_blog_url and soup:
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    text = a.get_text(strip=True).lower()
                    abs_link = make_absolute_url(final_root_url, href)
                    
                    if not is_same_domain(final_root_url, abs_link):
                        continue
                        
                    parsed_path = urlparse(abs_link).path.lower()
                    # Match path keywords or link text
                    if any(kw in parsed_path.strip("/").split("/") for kw in COMMON_BLOG_KEYWORDS) or any(text == kw for kw in COMMON_BLOG_KEYWORDS):
                        discovered_blog_url = abs_link
                        break

            if not discovered_blog_url:
                # Default guess: /blog
                blog_guess = make_absolute_url(final_root_url, "/blog")
                try:
                    b_resp = await client.get(blog_guess, headers=self.headers)
                    if b_resp.status_code == 200:
                        discovered_blog_url = blog_guess
                except Exception:
                    pass

            # 6. Analyze sample article signals if blog_url found
            target_page_for_signals = discovered_blog_url or final_root_url
            try:
                blog_resp = await client.get(target_page_for_signals, headers=self.headers)
                if blog_resp.status_code == 200:
                    bsoup = BeautifulSoup(blog_resp.text, "html.parser")
                    # Check JSON-LD
                    for script in bsoup.find_all("script", type="application/ld+json"):
                        if script.string and ("Article" in script.string or "BlogPosting" in script.string):
                            structured_metadata_available = True
                            if "datePublished" in script.string:
                                publication_date_available = True
                            break
                    if bsoup.find("link", rel="canonical"):
                        canonical_url_available = True
                    if bsoup.find("meta", property="article:published_time") or bsoup.find("time"):
                        publication_date_available = True
                        
                    # Find candidate article pattern
                    article_links = []
                    for a in bsoup.find_all("a", href=True):
                        link_abs = make_absolute_url(target_page_for_signals, a["href"])
                        p = urlparse(link_abs).path
                        parts = [segment for segment in p.strip("/").split("/") if segment]
                        if len(parts) >= 2 and any(k in parts[0] for k in ["blog", "article", "news", "post"]):
                            article_links.append(link_abs)
                    if article_links:
                        article_pattern = f"/{urlparse(article_links[0]).path.strip('/').split('/')[0]}/*"
            except Exception as e:
                logger.warning(f"Error checking article signals: {e}")

        # 7. Monitoring Strategy Selection
        selected_strategy = self.select_strategy(rss_available=rss_available, sitemap_available=sitemap_available, blog_url_available=bool(discovered_blog_url))

        return {
            "rss_available": rss_available,
            "rss_url": discovered_rss_url,
            "atom_available": atom_available,
            "sitemap_available": sitemap_available,
            "sitemap_url": discovered_sitemap_url,
            "sitemap_index": sitemap_is_index,
            "blog_url": discovered_blog_url,
            "article_pattern": article_pattern,
            "publication_date_available": publication_date_available,
            "structured_metadata_available": structured_metadata_available,
            "canonical_url_available": canonical_url_available,
            "selected_strategy": selected_strategy,
        }

    def select_strategy(self, rss_available: bool, sitemap_available: bool, blog_url_available: bool) -> str:
        """
        Determines the optimal strategy based on discovered sources.
        """
        if rss_available and sitemap_available:
            return "RSS + Sitemap"
        elif rss_available:
            return "RSS"
        elif sitemap_available and blog_url_available:
            return "Sitemap + Direct Page"
        elif sitemap_available:
            return "Sitemap"
        elif blog_url_available:
            return "Direct Page"
        return "Direct Page"
