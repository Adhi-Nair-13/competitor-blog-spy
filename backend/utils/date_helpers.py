import datetime
from typing import Optional, Tuple
from dateutil import parser as dateutil_parser

def ensure_utc(dt: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    """
    Ensures datetime is timezone-aware and converted to UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # If naive, assume UTC
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt

def parse_datetime(val) -> Optional[datetime.datetime]:
    """
    Robustly parses various datetime representations into a UTC datetime.
    Supports datetime objects, strings (ISO, RFC 2822, HTTP-date), and feedparser time structs.
    """
    if val is None:
        return None
    
    if isinstance(val, datetime.datetime):
        return ensure_utc(val)
        
    if isinstance(val, (int, float)):
        try:
            return datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
        except Exception:
            return None
            
    if hasattr(val, "tm_year"):  # time.struct_time from feedparser
        try:
            dt = datetime.datetime(*val[:6], tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            return None

    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        try:
            parsed = dateutil_parser.parse(val)
            return ensure_utc(parsed)
        except Exception:
            # Try dateparser fallback if needed
            try:
                import dateparser
                parsed = dateparser.parse(val)
                if parsed:
                    return ensure_utc(parsed)
            except Exception:
                pass
                
    return None

def calculate_detection_delay(published_at: Optional[datetime.datetime], detected_at: Optional[datetime.datetime]) -> Optional[float]:
    """
    Calculates detection delay in seconds: detected_at - published_at.
    Returns None if published_at is not available.
    """
    if not published_at or not detected_at:
        return None
        
    pub = ensure_utc(published_at)
    det = ensure_utc(detected_at)
    
    diff = (det - pub).total_seconds()
    # Guard against minor server clock skew resulting in negative delay
    return max(0.0, diff)

def format_detection_delay(delay_seconds: Optional[float]) -> str:
    """
    Formats the delay seconds into exact, human-readable format.
    Examples:
    - "42 seconds"
    - "2 minutes 15 seconds"
    - "8 minutes 41 seconds"
    - "1 hour 4 minutes"
    Never rounds to generic "under 5 minutes".
    """
    if delay_seconds is None:
        return "Publication time unavailable"
        
    total_seconds = int(round(delay_seconds))
    
    if total_seconds < 60:
        return f"{total_seconds} second{'s' if total_seconds != 1 else ''}"
        
    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    
    if minutes < 60:
        if remaining_seconds == 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        return f"{minutes} minute{'s' if minutes != 1 else ''} {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
        
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''} {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
        
    days = hours // 24
    remaining_hours = hours % 24
    if remaining_hours == 0:
        return f"{days} day{'s' if days != 1 else ''}"
    return f"{days} day{'s' if days != 1 else ''} {remaining_hours} hour{'s' if remaining_hours != 1 else ''}"

def get_delay_status(delay_seconds: Optional[float]) -> Tuple[str, str]:
    """
    Returns (status_label, color_code).
    GREEN: <= 300 seconds (5 minutes)
    YELLOW: > 300 seconds
    RED: Unavailable / Failed
    """
    if delay_seconds is None:
        return "UNAVAILABLE", "red"
    if delay_seconds <= 300:
        return "EXCELLENT (<= 5 min)", "green"
    return "DELAYED (> 5 min)", "yellow"
