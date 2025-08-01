"""
Real-time price fetcher for Indian stocks
Updates current prices while maintaining previous_close for change calculations
"""

import asyncio
import logging
import yfinance as yf
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.core.timezone_utils import get_ist_timestamp
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.models import Stock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimePriceFetcher:
    """
    Fetch real-time prices for Indian stocks while preserving previous_close
    """
    
    def __init__(self):
        self.update_interval = 300  # 5 minutes
        self.batch_size = 20  # Process in smaller batches for better performance
        
    async def get_real_time_price(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get real-time price for a single stock
        """
        try:
            # Determine yahoo symbol format
            if exchange == "BSE":
                yahoo_symbol = f"{symbol}.BO"
            else:
                yahoo_symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get current price and previous close
            hist = ticker.history(period="2d")
            
            if not hist.empty and len(hist) >= 1:
                current_price = float(hist['Close'].iloc[-1])
                
                # Get previous close (if we have 2 days of data)
                if len(hist) >= 2:
                    previous_close = float(hist['Close'].iloc[-2])
                else:
                    # Fallback to yesterday's close from info
                    info = ticker.info
                    previous_close = info.get('previousClose', current_price)
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'last_updated': get_ist_timestamp()
                }
            
        except Exception as e:
            logger.warning(f"Failed to get real-time price for {symbol}: {e}")
            
        return None
    
    async def update_stock_prices(self, stock_batch: List[Stock]) -> int:
        """
        Update prices for a batch of stocks
        """
        updated_count = 0
        db = SessionLocal()
        
        try:
            for stock in stock_batch:
                price_data = await self.get_real_time_price(stock.symbol, stock.exchange)
                
                if price_data:
                    # Store the old current_price as previous_close if it's the first update of the day
                    should_update_previous_close = self.should_update_previous_close(stock)
                    
                    if should_update_previous_close:
                        stock.previous_close = stock.current_price
                    
                    # Update current price
                    stock.current_price = price_data['current_price']
                    stock.last_updated = price_data['last_updated']
                    
                    updated_count += 1
                    
                    # Log significant price changes
                    if stock.previous_close and stock.previous_close > 0:
                        change_percent = ((stock.current_price - stock.previous_close) / stock.previous_close) * 100
                        if abs(change_percent) > 5:  # Log changes > 5%
                            logger.info(f"📈 {stock.symbol}: {change_percent:+.2f}% (₹{stock.current_price:.2f})")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            db.commit()
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating stock prices: {e}")
            db.rollback()
            return 0
        finally:
            db.close()
    
    def should_update_previous_close(self, stock: Stock) -> bool:
        """
        Determine if we should update the previous_close value
        Only update at start of new trading day or if previous_close is missing
        """
        if not stock.previous_close:
            return True
            
        if not stock.last_updated:
            return True
            
        # Check if it's a new trading day (simplified - just check if last update was yesterday)
        now = get_ist_timestamp()
        last_update = stock.last_updated
        
        # If last update was more than 18 hours ago, consider it a new trading day
        if (now - last_update).total_seconds() > 18 * 3600:
            return True
            
        return False
    
    async def update_popular_stocks(self, limit: int = 50) -> int:
        """
        Update prices for most popular/traded stocks only (faster updates)
        """
        logger.info(f"⚡ Quick update for top {limit} popular stocks...")
        
        db = SessionLocal()
        try:
            # Get most recently updated stocks (assuming they're more popular)
            popular_stocks = (
                db.query(Stock)
                .filter(Stock.is_active == True)
                .order_by(Stock.last_updated.desc())
                .limit(limit)
                .all()
            )
            
            updated = await self.update_stock_prices(popular_stocks)
            logger.info(f"⚡ Quick update completed: {updated}/{len(popular_stocks)} stocks updated")
            
            return updated
            
        except Exception as e:
            logger.error(f"Error in quick price update: {e}")
            return 0
        finally:
            db.close()

# Global instance
real_time_fetcher = RealTimePriceFetcher()

async def quick_price_update():
    """
    Quick update for popular stocks (can be called more frequently)
    """
    try:
        await real_time_fetcher.update_popular_stocks(50)
    except Exception as e:
        logger.error(f"Quick price update failed: {e}")
