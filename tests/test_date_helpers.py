from datetime import datetime, timezone, timedelta
from backend.utils.date_helpers import (
    calculate_detection_delay,
    format_detection_delay,
    get_delay_status,
    parse_datetime,
)

def test_date_parsing_various_formats():
    # ISO 8601
    dt1 = parse_datetime("2026-10-05T10:00:00Z")
    assert dt1 is not None
    assert dt1.tzinfo == timezone.utc

    # RFC 2822
    dt2 = parse_datetime("Mon, 05 Oct 2026 10:00:00 GMT")
    assert dt2 is not None
    assert dt2.year == 2026

    # None / Empty handling
    assert parse_datetime(None) is None
    assert parse_datetime("") is None
    assert parse_datetime("invalid-date-string-xyz") is None

def test_detection_delay_calculation():
    now = datetime(2026, 10, 5, 12, 5, 0, tzinfo=timezone.utc)
    published = datetime(2026, 10, 5, 12, 0, 0, tzinfo=timezone.utc)
    
    delay = calculate_detection_delay(published, now)
    assert delay == 300.0  # Exactly 5 minutes = 300 seconds

    # Delay formatting exactness (never rounded to generic 'under 5 minutes')
    assert format_detection_delay(42.0) == "42 seconds"
    assert format_detection_delay(135.0) == "2 minutes 15 seconds"
    assert format_detection_delay(521.0) == "8 minutes 41 seconds"
    assert format_detection_delay(3840.0) == "1 hour 4 minutes"
    assert format_detection_delay(None) == "Publication time unavailable"

def test_delay_status_benchmarks():
    status_label, color = get_delay_status(120.0)
    assert "EXCELLENT" in status_label
    assert color == "green"

    status_label, color = get_delay_status(450.0)
    assert "DELAYED" in status_label
    assert color == "yellow"

    status_label, color = get_delay_status(None)
    assert "UNAVAILABLE" in status_label
    assert color == "red"
