# utils.py
from datetime import datetime, timezone

def ensure_utc(dt):
    """
    Ensures that a datetime object is timezone-aware using UTC.
    If dt is naive, assigns UTC; otherwise, converts to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    else:
        return dt.astimezone(timezone.utc)

def utc_now():
    """
    Returns the current time in UTC.
    """
    return datetime.now(timezone.utc)
