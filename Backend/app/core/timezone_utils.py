"""
Timezone utilities for Indian Standard Time (IST)
"""
import pytz
from datetime import datetime
from typing import Optional
from app.core.config import settings

# Indian Standard Time zone
IST = pytz.timezone(settings.TIMEZONE)

def get_ist_now() -> datetime:
    """
    Get current datetime in Indian Standard Time (IST)
    """
    return datetime.now(IST)

def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST
    """
    if utc_dt.tzinfo is None:
        # If datetime is naive, assume it's UTC
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(IST)

def ist_to_utc(ist_dt: datetime) -> datetime:
    """
    Convert IST datetime to UTC
    """
    if ist_dt.tzinfo is None:
        # If datetime is naive, assume it's IST
        ist_dt = IST.localize(ist_dt)
    return ist_dt.astimezone(pytz.utc)

def format_ist_datetime(dt: Optional[datetime] = None, format_str: str = "%d/%m/%Y, %I:%M:%S %p") -> str:
    """
    Format datetime in IST with Indian format
    Default format: 30/7/2025, 6:01:32 am
    """
    if dt is None:
        dt = get_ist_now()
    
    # Convert to IST if needed
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    elif dt.tzinfo != IST:
        dt = dt.astimezone(IST)
    
    return dt.strftime(format_str)

def format_ist_for_api(dt: Optional[datetime] = None) -> str:
    """
    Format datetime in IST for API responses (JavaScript-friendly ISO format)
    Returns format like: '2025-07-30T11:47:24+05:30'
    
    IMPORTANT: This function assumes naive datetimes from database are in UTC
    and converts them to IST for proper display.
    """
    if dt is None:
        dt = get_ist_now()
    
    # Convert to IST if needed
    if dt.tzinfo is None:
        # Database timestamps are stored as naive UTC - convert to IST
        utc_dt = pytz.utc.localize(dt)
        dt = utc_dt.astimezone(IST)
    elif dt.tzinfo != IST:
        dt = dt.astimezone(IST)
    
    # Return ISO format with timezone info
    return dt.isoformat()

def get_ist_timestamp() -> datetime:
    """
    Get current timestamp in IST (timezone-aware)
    This is the recommended function for database timestamps
    """
    return get_ist_now()
