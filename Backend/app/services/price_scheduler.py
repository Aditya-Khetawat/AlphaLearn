"""
Background Scheduler for Real-time Stock Price Updates
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import threading
from contextlib import contextmanager

from app.services.market_timing import market_timer
from app.services.real_time_fetcher import real_time_fetcher
from app.core.database import get_db_session

logger = logging.getLogger(__name__)

class PriceUpdateScheduler:
    """Background scheduler for real-time price updates"""
    
    def __init__(self):
        self.is_running = False
        self.update_task: Optional[asyncio.Task] = None
        self.last_update_time: Optional[datetime] = None
        self.update_count = 0
        self.error_count = 0
        
        # Update intervals (in seconds)
        self.market_open_interval = 20  # 20 seconds during market hours
        self.market_closed_interval = 300  # 5 minutes when market is closed
        self.pre_market_interval = 60  # 1 minute during pre-market
    
    @contextmanager
    def get_db_session(self):
        """Get database session with proper cleanup - now using centralized context manager"""
        with get_db_session() as db:
            yield db
    
    async def _single_update_cycle(self):
        """Perform a single price update cycle"""
        try:
            # Get market status
            market_session = market_timer.get_market_session()
            
            # Determine which stocks to update based on market status
            if market_session.is_open:
                # Market is open - update active stocks
                logger.info("Market is open - performing active price update")
                
                with self.get_db_session() as db:
                    updated_count = await real_time_fetcher.update_database_prices(db)
                    
                self.update_count += updated_count
                self.last_update_time = datetime.now()
                
                logger.info(f"Updated {updated_count} stock prices (total updates: {self.update_count})")
                
            elif market_session.session_type == "pre_market":
                # Pre-market - update limited stocks
                logger.info("Pre-market session - performing limited price update")
                
                # Update only major stocks during pre-market
                major_symbols = ["TCS", "RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", 
                               "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK"]
                
                with self.get_db_session() as db:
                    updated_count = await real_time_fetcher.update_database_prices(db, major_symbols)
                
                self.update_count += updated_count
                self.last_update_time = datetime.now()
                
                logger.info(f"Pre-market: Updated {updated_count} major stock prices")
                
            else:
                # Market is closed - update only trending/popular stocks for homepage
                logger.info("Market is closed - updating trending stocks for homepage display")
                
                # Update only the most popular stocks that appear on homepage/trending
                trending_symbols = ["TCS", "RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", 
                                  "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK"]
                
                with self.get_db_session() as db:
                    updated_count = await real_time_fetcher.update_database_prices(db, trending_symbols)
                
                self.update_count += updated_count
                self.last_update_time = datetime.now()
                
                logger.info(f"Market closed: Updated {updated_count} trending stocks for homepage display")
                logger.info("💡 Other stocks will be updated on-demand when users search/select them")
        
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in price update cycle: {e}")
            
            # If too many errors, increase update interval
            if self.error_count > 5:
                logger.warning("Multiple update errors detected, slowing down updates")
                await asyncio.sleep(60)  # Wait 1 minute after errors
    
    def _get_update_interval(self) -> int:
        """Get the appropriate update interval based on market status"""
        market_session = market_timer.get_market_session()
        
        if market_session.is_open:
            return self.market_open_interval
        elif market_session.session_type == "pre_market":
            return self.pre_market_interval
        else:
            return self.market_closed_interval
    
    async def _update_loop(self):
        """Main update loop"""
        logger.info("Starting real-time price update scheduler")
        
        while self.is_running:
            try:
                # Perform update cycle
                await self._single_update_cycle()
                
                # Calculate next update interval
                interval = self._get_update_interval() 
                
                # Reset error count on successful update
                if self.error_count > 0:
                    self.error_count = max(0, self.error_count - 1)
                
                # Log status periodically
                if self.update_count % 10 == 0:
                    market_status = market_timer.get_market_status_message()
                    logger.info(f"Scheduler status - Updates: {self.update_count}, "
                              f"Errors: {self.error_count}, Market: {market_status['status']}")
                
                # Wait for next update
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Price update scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in update loop: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on unexpected errors
    
    def start_scheduler(self):
        """Start the background price update scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.update_count = 0
        self.error_count = 0
        
        # Start the update loop in a new thread to avoid blocking
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.update_task = loop.create_task(self._update_loop())
                loop.run_until_complete(self.update_task)
            except Exception as e:
                logger.error(f"Error in async update loop: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async_loop, daemon=True)
        thread.start()
        
        logger.info("Price update scheduler started in background thread")
    
    def stop_scheduler(self):
        """Stop the background price update scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
        
        logger.info("Price update scheduler stopped")
    
    def get_scheduler_status(self) -> Dict[str, any]:
        """Get current scheduler status"""
        market_status = market_timer.get_market_status_message()
        
        return {
            "scheduler_running": self.is_running,
            "last_update": self.last_update_time.isoformat() if self.last_update_time else None,
            "total_updates": self.update_count,
            "error_count": self.error_count,
            "update_interval": self._get_update_interval(),
            "market_status": market_status
        }

# Global scheduler instance
price_scheduler = PriceUpdateScheduler()
