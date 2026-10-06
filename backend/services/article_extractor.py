import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from bs4 import BeautifulSoup
import trafilatura

from backend.config import settings
from backend.utils.url_helpers import normalize_url, make_absolute_url
from backend.utils.date_helpers import parse_datetime, ensure_utc
from backend.utils.security import sanitize_html, validate_target_url

logger = logging.getLogger(__name__)

class ArticleExtractor:
    """
    Extracts article metadata and clean content body from an article webpage.
    Supports JSON-LD structured data, OpenGraph, microdata, semantic HTML, and trafilatura.
    """
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def fetch_and_extract(self, url: str) -> Dict[str, Any]:
        """
        Fetches the web page and extracts structured article information.
        """
        valid_url = validate_target_url(url)
        normalized_url = normalize_url(valid_url)
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(normalized_url, headers=self.headers)
            response.raise_for_status()
            html_content = response.text
            final_url = str(response.url)

        return self.extract_from_html(html_content, base_url=final_url)

    def extract_from_html(self, html: str, base_url: str) -> Dict[str, Any]:
        """
        Extracts all relevant metadata from raw HTML.
        """
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")
        
        # 1. Structured Data JSON-LD
        json_ld_data = self._extract_json_ld(soup)
        
        # 2. Canonical URL
        canonical_url = self._extract_canonical(soup, base_url, json_ld_data)
        
        # 3. Title
        title = self._extract_title(soup, json_ld_data)
        
        # 4. Publication date
        published_at = self._extract_publication_date(soup, json_ld_data)
        
        # 5. Author
        author = self._extract_author(soup, json_ld_data)
        
        # 6. Meta Description
        meta_description = self._extract_meta_description(soup, json_ld_data)
        
        # 7. Featured Image
        featured_image = self._extract_featured_image(soup, base_url, json_ld_data)
        
        # 8. Categories and Tags
        categories, tags = self._extract_categories_and_tags(soup, json_ld_data)
        
        # 9. Main article content using trafilatura with BeautifulSoup fallback
        content = self._extract_content(html, soup)
        
        # 10. Relevant Links inside article
        relevant_links = self._extract_relevant_links(soup, base_url)

        return {
            "title": title or "Untitled Article",
            "content": sanitize_html(content) if content else "",
            "author": author,
            "published_at": published_at,
            "canonical_url": canonical_url,
            "source_url": normalize_url(base_url),
            "meta_description": meta_description,
            "featured_image": featured_image,
            "categories": ", ".join(categories) if categories else None,
            "tags": ", ".join(tags) if tags else None,
            "relevant_links": json.dumps(relevant_links) if relevant_links else None,
        }

    def _extract_json_ld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extracts Article, BlogPosting, or NewsArticle from schema.org JSON-LD scripts.
        """
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
                if isinstance(data, list):
                    for item in data:
                        if self._is_article_schema(item):
                            return item
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        for item in data["@graph"]:
                            if self._is_article_schema(item):
                                return item
                    elif self._is_article_schema(data):
                        return data
            except Exception:
                continue
        return {}

    def _is_article_schema(self, item: Any) -> bool:
        if not isinstance(item, dict):
            return False
        item_type = item.get("@type", "")
        if isinstance(item_type, list):
            return any(t in ["Article", "BlogPosting", "NewsArticle", "TechArticle", "SocialMediaPosting"] for t in item_type)
        return item_type in ["Article", "BlogPosting", "NewsArticle", "TechArticle", "SocialMediaPosting"]

    def _extract_canonical(self, soup: BeautifulSoup, base_url: str, json_ld: Dict[str, Any]) -> str:
        # Check link rel="canonical"
        link_tag = soup.find("link", rel=lambda val: val and "canonical" in val.lower())
        if link_tag and link_tag.get("href"):
            return normalize_url(make_absolute_url(base_url, link_tag["href"]))
            
        # Check JSON-LD mainEntityOfPage or url
        if json_ld:
            url = json_ld.get("url") or (json_ld.get("mainEntityOfPage", {}).get("@id") if isinstance(json_ld.get("mainEntityOfPage"), dict) else json_ld.get("mainEntityOfPage"))
            if url and isinstance(url, str):
                return normalize_url(make_absolute_url(base_url, url))
                
        # Check og:url
        og_url = soup.find("meta", property="og:url")
        if og_url and og_url.get("content"):
            return normalize_url(make_absolute_url(base_url, og_url["content"]))
            
        return normalize_url(base_url)

    def _extract_title(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> str:
        # 1. JSON-LD headline
        if json_ld and json_ld.get("headline"):
            return str(json_ld["headline"]).strip()
            
        # 2. OpenGraph og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # 3. Twitter title
        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        if tw_title and tw_title.get("content"):
            return tw_title["content"].strip()
            
        # 4. First <h1> tag
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
            
        # 5. HTML <title> tag
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            raw = title_tag.get_text(strip=True)
            # Strip common suffixes like " | Company Name"
            return raw.split(" | ")[0].split(" - ")[0].strip()
            
        return ""

    def _extract_publication_date(self, soup: BeautifulSoup, json_ld: Dict[str, Any]):
        # 1. JSON-LD datePublished or dateCreated
        if json_ld:
            for key in ["datePublished", "dateCreated", "dateModified"]:
                if json_ld.get(key):
                    parsed = parse_datetime(json_ld[key])
                    if parsed:
                        return parsed
                        
        # 2. OpenGraph article:published_time
        for prop in ["article:published_time", "og:published_time", "publication_date", "date"]:
            meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
            if meta and meta.get("content"):
                parsed = parse_datetime(meta["content"])
                if parsed:
                    return parsed
                    
        # 3. <time> tag with datetime attribute
        for time_tag in soup.find_all("time"):
            datetime_attr = time_tag.get("datetime") or time_tag.get("pubdate") or time_tag.get_text(strip=True)
            if datetime_attr:
                parsed = parse_datetime(datetime_attr)
                if parsed:
                    return parsed
                    
        # 4. Fallback: return None if publication date cannot be reliably determined
        # "Do not invent missing information. If publication date cannot be reliably determined, store it as null"
        return None

    def _extract_author(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> Optional[str]:
        if json_ld and json_ld.get("author"):
            author_val = json_ld["author"]
            if isinstance(author_val, dict):
                return author_val.get("name")
            elif isinstance(author_val, list) and len(author_val) > 0:
                first = author_val[0]
                return first.get("name") if isinstance(first, dict) else str(first)
            elif isinstance(author_val, str):
                return author_val

        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", property="article:author")
        if meta_author and meta_author.get("content"):
            return meta_author["content"].strip()
            
        author_elem = soup.find(class_=lambda c: c and any(sub in c.lower() for sub in ["author", "byline", "author-name"]))
        if author_elem:
            text = author_elem.get_text(strip=True)
            # Remove "By " prefix if present
            if text.lower().startswith("by "):
                text = text[3:].strip()
            if text and len(text) < 100:
                return text

        return None

    def _extract_meta_description(self, soup: BeautifulSoup, json_ld: Dict[str, Any]) -> Optional[str]:
        if json_ld and json_ld.get("description"):
            return str(json_ld["description"]).strip()
            
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()
            
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()
            
        return None

    def _extract_featured_image(self, soup: BeautifulSoup, base_url: str, json_ld: Dict[str, Any]) -> Optional[str]:
        if json_ld and json_ld.get("image"):
            img = json_ld["image"]
            if isinstance(img, dict) and img.get("url"):
                return make_absolute_url(base_url, img["url"])
            elif isinstance(img, str):
                return make_absolute_url(base_url, img)
            elif isinstance(img, list) and len(img) > 0:
                first = img[0]
                return make_absolute_url(base_url, first.get("url") if isinstance(first, dict) else str(first))

        og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if og_img and og_img.get("content"):
            return make_absolute_url(base_url, og_img["content"])
            
        # Look for leading article image
        article_elem = soup.find("article") or soup.find("main")
        if article_elem:
            img = article_elem.find("img")
            if img and img.get("src"):
                return make_absolute_url(base_url, img["src"])

        return None

    def _extract_categories_and_tags(self, soup: BeautifulSoup, json_ld: Dict[str, Any]):
        categories = []
        tags = []
        
        if json_ld:
            if json_ld.get("articleSection"):
                sect = json_ld["articleSection"]
                if isinstance(sect, list):
                    categories.extend([str(s).strip() for s in sect])
                elif isinstance(sect, str):
                    categories.append(sect.strip())
            if json_ld.get("keywords"):
                kw = json_ld["keywords"]
                if isinstance(kw, list):
                    tags.extend([str(k).strip() for k in kw])
                elif isinstance(kw, str):
                    tags.extend([k.strip() for k in kw.split(",") if k.strip()])
                    
        # Meta tags
        meta_kw = soup.find("meta", attrs={"name": "keywords"})
        if meta_kw and meta_kw.get("content"):
            tags.extend([k.strip() for k in meta_kw["content"].split(",") if k.strip()])
            
        # Deduplicate
        return list(dict.fromkeys(categories)), list(dict.fromkeys(tags))

    def _extract_content(self, raw_html: str, soup: BeautifulSoup) -> str:
        # 1. Try Trafilatura for clean extraction
        try:
            extracted = trafilatura.extract(raw_html, include_formatting=True, include_images=True)
            if extracted and len(extracted.strip()) > 50:
                return extracted.strip()
        except Exception:
            pass

        # 2. Fallback to semantic container
        target_container = soup.find("article") or soup.find("main") or soup.find(class_=lambda c: c and any(w in c.lower() for w in ["article-body", "post-content", "entry-content"]))
        if target_container:
            # clean scripts & styles
            for elem in target_container(["script", "style", "nav", "footer", "form"]):
                elem.decompose()
            return target_container.get_text(separator="\n", strip=True)
            
        # 3. Fallback body text
        body = soup.find("body")
        if body:
            for elem in body(["script", "style", "nav", "footer", "header", "form"]):
                elem.decompose()
            return body.get_text(separator="\n", strip=True)
            
        return ""

    def _extract_relevant_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        container = soup.find("article") or soup.find("main") or soup
        for a in container.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = make_absolute_url(base_url, href)
            if abs_url and abs_url not in links:
                links.append(abs_url)
            if len(links) >= 20:
                break
        return links
