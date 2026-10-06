import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from backend.config import settings

BLOCKED_SCHEMES = {"file", "ftp", "gopher", "data", "javascript", "vbscript"}
PRIVATE_HOSTS = {"169.254.169.254", "metadata.google.internal"}

def validate_target_url(url: str, allow_local: bool = True) -> str:
    """
    Validates that a URL is safe to scrape.
    Ensures http/https scheme and blocks known cloud metadata addresses.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")
        
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"Unsupported protocol scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")
        
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("Invalid URL: missing host name.")
        
    if hostname in PRIVATE_HOSTS:
        raise ValueError("Access to internal cloud metadata endpoints is prohibited.")
        
    # In production non-demo mode, disallow localhost/127.0.0.1 to avoid SSRF
    if not settings.DEMO_MODE and not allow_local:
        if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or hostname.startswith("192.168.") or hostname.startswith("10."):
            raise ValueError("Access to private/local network addresses is restricted.")
            
    return url

def sanitize_html(html_content: str) -> str:
    """
    Removes script tags, iframe, object, embed, and dangerous inline JS attributes.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove executable tags
    for tag in soup(["script", "style", "iframe", "object", "embed", "applet", "noscript", "form"]):
        tag.decompose()
        
    # Remove javascript attributes like onclick, onload, etc.
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        for attr, val in attrs.items():
            if attr.lower().startswith("on") or (isinstance(val, str) and "javascript:" in val.lower()):
                del tag.attrs[attr]
                
    return str(soup)
