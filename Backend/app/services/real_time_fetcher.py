"""
Real-time Indian Stock Price Fetcher with Rate Limiting
"""
import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import time
import json
from sqlalchemy.orm import Session
import requests

from app.services.market_timing import market_timer
from app.models.models import Stock

logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """Stock price data structure"""
    symbol: str
    current_price: float
    previous_close: float
    price_change: float
    price_change_percent: float
    volume: Optional[int] = None
    last_updated: datetime = None
    
class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window  # in seconds
        self.calls = []
        
    async def acquire(self):
        """Wait if necessary to respect rate limits"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        # If we're at the limit, wait
        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            sleep_time = self.time_window - (now - oldest_call) + 0.1
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)

class RealTimePriceFetcher:
    """Fetches real-time stock prices with rate limiting and error handling"""
    
    def __init__(self):
        # Rate limiters for different data sources
        self.yahoo_limiter = RateLimiter(max_calls=100, time_window=60)  # 100 calls per minute
        
        # Cache for recent price data
        self.price_cache: Dict[str, PriceData] = {}
        self.cache_timeout = 30  # seconds
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delays = [1, 2, 5]  # seconds
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid"""
        if symbol not in self.price_cache:
            return False
        
        cached_data = self.price_cache[symbol]
        if cached_data.last_updated is None:
            return False
        
        age = (datetime.now() - cached_data.last_updated).total_seconds()
        return age < self.cache_timeout
    
    async def _fetch_yahoo_finance_batch(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Fetch multiple stocks from Yahoo Finance with rate limiting"""
        await self.yahoo_limiter.acquire()
        
        results = {}
        
        try:
            # Convert Indian symbols to Yahoo Finance format
            yahoo_symbols = []
            symbol_mapping = {}
            
            for symbol in symbols:
                if symbol.endswith('.NS') or symbol.endswith('.BO'):
                    yahoo_symbol = symbol
                else:
                    # Try both NSE and BSE formats for better coverage
                    yahoo_symbol = f"{symbol}.NS"
                
                yahoo_symbols.append(yahoo_symbol)
                symbol_mapping[yahoo_symbol] = symbol
                
                # Also try BSE format as fallback
                if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                    bse_symbol = f"{symbol}.BO"
                    yahoo_symbols.append(bse_symbol)
                    symbol_mapping[bse_symbol] = symbol
            
            # Fetch data in batches to avoid overwhelming the API
            batch_size = 10
            for i in range(0, len(yahoo_symbols), batch_size):
                batch_symbols = yahoo_symbols[i:i + batch_size]
                
                try:
                    # Use different intervals based on market status
                    # For closed market, get daily data to calculate proper daily changes
                    market_session = market_timer.get_market_session()
                    
                    if market_session.is_open:
                        # Market open - get minute data for real-time prices
                        data = yf.download(
                            tickers=batch_symbols,
                            period="2d",
                            interval="1m",
                            group_by="ticker",
                            auto_adjust=True,
                            prepost=True,
                            threads=True,
                            progress=False
                        )
                    else:
                        # Market closed - get daily data for proper daily changes
                        data = yf.download(
                            tickers=batch_symbols,
                            period="5d",  # Get 5 days to ensure we have previous close
                            interval="1d",  # Daily intervals for proper close-to-close changes
                            group_by="ticker",
                            auto_adjust=True,
                            prepost=False,
                            threads=True,
                            progress=False
                        )
                    
                    current_time = datetime.now()
                    
                    for yahoo_symbol in batch_symbols:
                        original_symbol = symbol_mapping[yahoo_symbol]
                        
                        try:
                            if len(batch_symbols) == 1:
                                symbol_data = data
                            else:
                                symbol_data = data[yahoo_symbol] if yahoo_symbol in data.columns.get_level_values(0) else None
                            
                            if symbol_data is not None and not symbol_data.empty:
                                # Get the latest data point
                                latest_data = symbol_data.iloc[-1]
                                
                                # Handle multi-level columns for single symbol downloads
                                def get_field_value(data_row, field_name):
                                    """Helper to get field value from potentially multi-level columns"""
                                    if len(batch_symbols) == 1:
                                        # Single symbol download - multi-level columns
                                        col_key = (yahoo_symbol, field_name)
                                        if col_key in data_row.index:
                                            return data_row[col_key]
                                        # Fallback: try simple field name
                                        if field_name in data_row.index:
                                            return data_row[field_name]
                                    else:
                                        # Multi-symbol download - simple columns
                                        if field_name in data_row.index:
                                            return data_row[field_name]
                                    return None
                                
                                # Get current price
                                close_value = get_field_value(latest_data, 'Close')
                                if close_value is None or pd.isna(close_value):
                                    logger.warning(f"No close price data for {yahoo_symbol}")
                                    continue
                                    
                                current_price = float(close_value)
                                
                                # Get previous close price
                                if len(symbol_data) >= 2:
                                    # Use the previous day's close price
                                    prev_data = symbol_data.iloc[-2]
                                    prev_close_value = get_field_value(prev_data, 'Close')
                                    if prev_close_value is not None and not pd.isna(prev_close_value):
                                        previous_close = float(prev_close_value)
                                    else:
                                        # Fallback: use open price of current day
                                        open_value = get_field_value(latest_data, 'Open')
                                        if open_value is not None and not pd.isna(open_value):
                                            previous_close = float(open_value)
                                        else:
                                            previous_close = current_price  # Last resort
                                else:
                                    # Fallback: use open price of current day
                                    open_value = get_field_value(latest_data, 'Open')
                                    if open_value is not None and not pd.isna(open_value):
                                        previous_close = float(open_value)
                                    else:
                                        previous_close = current_price  # Last resort
                                
                                # Calculate changes
                                price_change = current_price - previous_close
                                price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
                                
                                volume_value = get_field_value(latest_data, 'Volume')
                                volume = int(volume_value) if volume_value is not None and not pd.isna(volume_value) else None
                                
                                # Only use the first successful result for each original symbol
                                if original_symbol not in results:
                                    results[original_symbol] = PriceData(
                                        symbol=original_symbol,
                                        current_price=current_price,
                                        previous_close=previous_close,
                                        price_change=price_change,
                                        price_change_percent=price_change_percent,
                                        volume=volume,
                                        last_updated=current_time
                                    )
                                    logger.info(f"✅ Updated {original_symbol}: ₹{current_price:.2f} ({price_change_percent:+.2f}%)")
                            else:
                                logger.debug(f"No data available for {yahoo_symbol}")
                        
                        except Exception as e:
                            logger.warning(f"Error processing {yahoo_symbol}: {e}")
                            continue
                
                except Exception as e:
                    logger.error(f"Error fetching batch {batch_symbols}: {e}")
                    continue
                
                # Small delay between batches
                await asyncio.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error in Yahoo Finance batch fetch: {e}")
        
        return results
    
    async def _fetch_with_retry(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Fetch prices with retry mechanism"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.retry_delays[min(attempt - 1, len(self.retry_delays) - 1)]
                    logger.info(f"Retrying price fetch after {delay} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                
                return await self._fetch_yahoo_finance_batch(symbols)
            
            except Exception as e:
                last_error = e
                logger.warning(f"Price fetch attempt {attempt + 1} failed: {e}")
        
        logger.error(f"All price fetch attempts failed. Last error: {last_error}")
        return {}
    
    async def get_real_time_prices(self, symbols: List[str], force_refresh: bool = False) -> Dict[str, PriceData]:
        """Get real-time prices for multiple symbols"""
        results = {}
        symbols_to_fetch = []
        
        # Check cache first
        for symbol in symbols:
            if not force_refresh and self._is_cache_valid(symbol):
                results[symbol] = self.price_cache[symbol]
            else:
                symbols_to_fetch.append(symbol)
        
        # Fetch uncached symbols
        if symbols_to_fetch:
            logger.info(f"Fetching real-time prices for {len(symbols_to_fetch)} symbols")
            fresh_data = await self._fetch_with_retry(symbols_to_fetch)
            
            # Update cache and results
            for symbol, price_data in fresh_data.items():
                self.price_cache[symbol] = price_data
                results[symbol] = price_data
        
        return results
    
    async def update_database_prices(self, db: Session, symbols: List[str] = None) -> int:
        """Update stock prices in database"""
        try:
            # Get stocks to update
            query = db.query(Stock).filter(Stock.is_active == True)
            
            if symbols:
                query = query.filter(Stock.symbol.in_(symbols))
            else:
                # Update top 100 most active stocks during market hours
                query = query.order_by(Stock.market_cap.desc() if hasattr(Stock, 'market_cap') else Stock.id)
            
            stocks = query.limit(100).all()
            
            if not stocks:
                return 0
            
            symbols_to_update = [stock.symbol for stock in stocks]
            logger.info(f"Updating prices for {len(symbols_to_update)} stocks")
            
            # Fetch real-time prices
            price_data = await self.get_real_time_prices(symbols_to_update, force_refresh=True)
            
            # Update database
            updated_count = 0
            current_time = datetime.now()
            
            for stock in stocks:
                if stock.symbol in price_data:
                    data = price_data[stock.symbol]
                    
                    # Update stock fields
                    stock.current_price = data.current_price
                    stock.previous_close = data.previous_close
                    stock.price_change = data.price_change
                    stock.price_change_percent = data.price_change_percent
                    
                    if data.volume is not None:
                        stock.volume = data.volume
                    
                    stock.last_updated = current_time
                    updated_count += 1
            
            # Commit changes
            db.commit()
            logger.info(f"Successfully updated {updated_count} stock prices")
            
            return updated_count
        
        except Exception as e:
            logger.error(f"Error updating database prices: {e}")
            db.rollback()
            return 0

# Global instance
real_time_fetcher = RealTimePriceFetcher()
