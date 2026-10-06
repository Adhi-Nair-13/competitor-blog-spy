import re
from urllib.parse import urlparse, urlunparse, urljoin, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "mc_cid", "mc_eid", "source", "_hsenc", "_hsmi"
}

def normalize_url(url: str) -> str:
    """
    Normalizes a URL by lowercasing scheme and host, stripping trailing slashes
    from standard paths, and removing common analytics/tracking query params.
    """
    if not url:
        return ""
    
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Strip standard port
    if (scheme == "http" and netloc.endswith(":80")) or (scheme == "https" and netloc.endswith(":443")):
        netloc = netloc.rsplit(":", 1)[0]
        
    path = parsed.path
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    if not path:
        path = "/"
        
    # Filter out tracking query parameters
    query_tuples = parse_qsl(parsed.query, keep_blank_values=True)
    filtered_query = [(k, v) for k, v in query_tuples if k.lower() not in TRACKING_PARAMS]
    query = urlencode(filtered_query)
    
    # We strip fragments for canonical uniqueness
    return urlunparse((scheme, netloc, path, parsed.params, query, ""))

def make_absolute_url(base_url: str, link: str) -> str:
    """
    Converts a relative link to an absolute URL based on base_url.
    """
    if not link:
        return ""
    link = link.strip()
    return normalize_url(urljoin(base_url, link))

def get_domain(url: str) -> str:
    """
    Extracts the root host/domain from a URL.
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""

def is_same_domain(url1: str, url2: str) -> bool:
    """
    Checks whether two URLs share the same domain or subdomain.
    """
    d1 = get_domain(url1).replace("www.", "")
    d2 = get_domain(url2).replace("www.", "")
    return d1 == d2 or d1.endswith("." + d2) or d2.endswith("." + d1)
