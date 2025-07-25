"""
Timezone utilities for handling datetime conversions across different timezones.
Implements the requirement for timezone management with IST as base.
"""

from datetime import datetime,timedelta
from typing import Optional
import pytz
from app.config import settings


class TimezoneManager:
    """Handles timezone conversions and management."""
    
    def __init__(self):
        self.default_tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    
    def localize_datetime(self, dt: datetime, timezone: Optional[str] = None) -> datetime:
        """
        Localize a naive datetime to specified timezone.
        
        Args:
            dt: Naive datetime object
            timezone: Target timezone string (defaults to IST)
            
        Returns:
            Timezone-aware datetime object
        """
        if timezone:
            tz = pytz.timezone(timezone)
        else:
            tz = self.default_tz
            
        if dt.tzinfo is None:
            return tz.localize(dt)
        return dt.astimezone(tz)
    
    def convert_timezone(self, dt: datetime, target_timezone: str) -> datetime:
        """
        Convert datetime from one timezone to another.
        
        Args:
            dt: Source datetime (should be timezone-aware)
            target_timezone: Target timezone string
            
        Returns:
            Datetime converted to target timezone
        """
        if dt.tzinfo is None:
            # If naive, assume it's in default timezone
            dt = self.default_tz.localize(dt)
        
        target_tz = pytz.timezone(target_timezone)
        return dt.astimezone(target_tz)
    
    def get_current_time(self, timezone: Optional[str] = None) -> datetime:
        """Get current time in specified timezone."""
        tz = pytz.timezone(timezone) if timezone else self.default_tz
        return datetime.now(tz)
    
    def get_one_day_aheadtime(self, timezone: Optional[str] = None) -> datetime:
        """Get current time in specified timezone."""
        tz = pytz.timezone(timezone) if timezone else self.default_tz
        return datetime.now(tz)+timedelta(days=1)

# Global timezone manager instance
tz_manager = TimezoneManager()