"""
Indian Stock Market Timing and Holiday Management
"""
import pytz
from datetime import datetime, time, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MarketSession:
    """Represents a market trading session"""
    is_open: bool
    next_open: Optional[datetime]
    next_close: Optional[datetime]
    session_type: str  # "regular", "pre_market", "after_market", "closed"
    time_until_next: Optional[timedelta]

class IndianMarketTimer:
    """Manages Indian stock market timing and holidays"""
    
    def __init__(self):
        self.ist_tz = pytz.timezone('Asia/Kolkata')
        
        # NSE/BSE trading hours (IST)
        self.market_open_time = time(9, 15)  # 9:15 AM
        self.market_close_time = time(15, 30)  # 3:30 PM
        
        # Pre-market session (optional)
        self.pre_market_open = time(9, 0)   # 9:00 AM
        self.pre_market_close = time(9, 15)  # 9:15 AM
        
        # Market holidays for 2025 (major ones)
        self.market_holidays_2025 = {
            # Republic Day
            "2025-01-26": "Republic Day",
            # Holi
            "2025-03-14": "Holi",
            # Good Friday
            "2025-04-18": "Good Friday",
            # Ram Navami
            "2025-04-06": "Ram Navami",
            # Maharashtra Day
            "2025-05-01": "Maharashtra Day",
            # Independence Day
            "2025-08-15": "Independence Day",
            # Ganesh Chaturthi
            "2025-08-29": "Ganesh Chaturthi",
            # Gandhi Jayanti
            "2025-10-02": "Gandhi Jayanti",
            # Diwali Balipratipada
            "2025-11-01": "Diwali Balipratipada",
            # Guru Nanak Jayanti
            "2025-11-05": "Guru Nanak Jayanti",
            # Christmas
            "2025-12-25": "Christmas"
        }
    
    def get_current_ist_time(self) -> datetime:
        """Get current time in IST"""
        return datetime.now(self.ist_tz)
    
    def is_market_holiday(self, date: datetime) -> Tuple[bool, Optional[str]]:
        """Check if given date is a market holiday"""
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.market_holidays_2025:
            return True, self.market_holidays_2025[date_str]
        return False, None
    
    def is_weekend(self, date: datetime) -> bool:
        """Check if given date is weekend (Saturday=5, Sunday=6)"""
        return date.weekday() >= 5
    
    def is_trading_day(self, date: datetime) -> bool:
        """Check if given date is a trading day"""
        if self.is_weekend(date):
            return False
        
        is_holiday, _ = self.is_market_holiday(date)
        return not is_holiday
    
    def get_market_session(self, current_time: Optional[datetime] = None) -> MarketSession:
        """Get current market session information"""
        if current_time is None:
            current_time = self.get_current_ist_time()
        
        current_date = current_time.date()
        current_time_only = current_time.time()
        
        # Check if today is a trading day
        if not self.is_trading_day(current_time):
            return self._get_closed_market_session(current_time, "holiday_weekend")
        
        # Check market hours
        if self.market_open_time <= current_time_only <= self.market_close_time:
            # Market is open
            next_close = datetime.combine(current_date, self.market_close_time)
            next_close = self.ist_tz.localize(next_close)
            
            return MarketSession(
                is_open=True,
                next_open=None,
                next_close=next_close,
                session_type="regular",
                time_until_next=next_close - current_time
            )
        
        elif self.pre_market_open <= current_time_only < self.market_open_time:
            # Pre-market session
            next_open = datetime.combine(current_date, self.market_open_time)
            next_open = self.ist_tz.localize(next_open)
            
            return MarketSession(
                is_open=False,
                next_open=next_open,
                next_close=None,
                session_type="pre_market",
                time_until_next=next_open - current_time
            )
        
        else:
            # Market closed (after hours or before pre-market)
            return self._get_closed_market_session(current_time, "closed")
    
    def _get_closed_market_session(self, current_time: datetime, reason: str) -> MarketSession:
        """Get market session for when market is closed"""
        next_trading_day = self._get_next_trading_day(current_time)
        next_open = datetime.combine(next_trading_day, self.market_open_time)
        next_open = self.ist_tz.localize(next_open)
        
        return MarketSession(
            is_open=False,
            next_open=next_open,
            next_close=None,
            session_type=reason,
            time_until_next=next_open - current_time
        )
    
    def _get_next_trading_day(self, current_time: datetime) -> datetime.date:
        """Find the next trading day"""
        next_day = current_time.date() + timedelta(days=1)
        
        # If current time is before market open today and today is trading day
        if (current_time.time() < self.market_open_time and 
            self.is_trading_day(current_time)):
            next_day = current_time.date()
        
        # Find next trading day
        while not self.is_trading_day(datetime.combine(next_day, self.market_open_time)):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_market_status_message(self) -> Dict[str, any]:
        """Get human-readable market status"""
        session = self.get_market_session()
        current_time = self.get_current_ist_time()
        
        if session.is_open:
            closes_in = session.time_until_next
            hours, remainder = divmod(closes_in.total_seconds(), 3600)
            minutes = remainder // 60
            
            return {
                "status": "open",
                "message": f"Market is OPEN - Closes in {int(hours)}h {int(minutes)}m",
                "next_event": "market_close",
                "next_event_time": session.next_close.isoformat(),
                "session_type": session.session_type
            }
        
        else:
            opens_in = session.time_until_next
            
            if opens_in.days > 0:
                return {
                    "status": "closed",
                    "message": f"Market CLOSED - Opens in {opens_in.days} days",
                    "next_event": "market_open",
                    "next_event_time": session.next_open.isoformat(),
                    "session_type": session.session_type
                }
            else:
                hours, remainder = divmod(opens_in.total_seconds(), 3600)
                minutes = remainder // 60
                
                return {
                    "status": "closed",
                    "message": f"Market CLOSED - Opens in {int(hours)}h {int(minutes)}m",
                    "next_event": "market_open", 
                    "next_event_time": session.next_open.isoformat(),
                    "session_type": session.session_type
                }

# Global instance
market_timer = IndianMarketTimer()
