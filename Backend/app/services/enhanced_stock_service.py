"""
Enhanced Stock Management Service for AlphaLearn
Inspired by the comprehensive StockManagement.py approach

This service provides:
1. Multiple data source fetching (NSE API, Yahoo Finance, fallback lists)
2. Automatic daily updates via scheduler
3. Advanced search with pagination
4. Background task processing
5. Production-ready error handling
6. Comprehensive API endpoints
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import requests
import yfinance as yf
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import time

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    AsyncIOScheduler = None

from app.core.database import SessionLocal
from app.models.models import Stock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedStockDataFetcher:
    """Enhanced stock data fetcher using multiple free sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    async def fetch_nse_api_stocks(self) -> List[Dict[str, Any]]:
        """Fetch stocks from NSE public API (following your approach)"""
        try:
            # NSE indices for comprehensive coverage
            indices = [
                'NIFTY%20500',
                'NIFTY%20TOTAL%20MARKET', 
                'NIFTY%20SMALLCAP%20100',
                'NIFTY%20MIDCAP%20100'
            ]
            
            all_stocks = []
            
            for index in indices:
                try:
                    url = f'https://www.nseindia.com/api/equity-stockIndices?index={index}'
                    logger.info(f"Fetching from NSE: {index.replace('%20', ' ')}")
                    
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for stock in data.get('data', []):
                            all_stocks.append({
                                'symbol': stock['symbol'],
                                'name': stock.get('companyName', stock['symbol']),
                                'exchange': 'NSE',
                                'last_price': stock.get('lastPrice'),
                                'market_cap': stock.get('totalTradedValue'),
                                'sector': 'Unknown'  # NSE API doesn't provide sector
                            })
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error fetching NSE index {index}: {e}")
                    continue
            
            # Remove duplicates
            unique_stocks = {}
            for stock in all_stocks:
                unique_stocks[stock['symbol']] = stock
            
            logger.info(f"Fetched {len(unique_stocks)} unique stocks from NSE API")
            return list(unique_stocks.values())
            
        except Exception as e:
            logger.error(f"Error in NSE API fetch: {e}")
            return []
    
    async def fetch_yahoo_finance_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Fetch stock data using yfinance (following your batch approach)"""
        try:
            stocks = []
            batch_size = 20
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                yahoo_symbols = [f"{symbol}.NS" for symbol in batch]
                
                try:
                    # Use yfinance to get detailed data
                    data = yf.download(yahoo_symbols, period="2d", progress=False)
                    
                    if not data.empty:
                        for j, symbol in enumerate(batch):
                            yahoo_symbol = yahoo_symbols[j]
                            
                            try:
                                # Get ticker info for additional details
                                ticker = yf.Ticker(yahoo_symbol)
                                info = ticker.info
                                
                                # Get price data
                                if len(batch) == 1:
                                    close_data = data['Close'] if 'Close' in data.columns else data
                                else:
                                    close_data = data[yahoo_symbol]['Close'] if yahoo_symbol in data.columns.levels[0] else None
                                
                                current_price = float(close_data.iloc[-1]) if close_data is not None and not close_data.empty else info.get('currentPrice', 0)
                                
                                stocks.append({
                                    'symbol': symbol,
                                    'name': info.get('longName', info.get('shortName', symbol)),
                                    'exchange': 'NSE',
                                    'sector': info.get('sector', 'Unknown'),
                                    'market_cap': info.get('marketCap'),
                                    'last_price': current_price
                                })
                                
                            except Exception as e:
                                logger.warning(f"Error processing {symbol}: {e}")
                                # Add basic info even if detailed fetch fails
                                stocks.append({
                                    'symbol': symbol,
                                    'name': symbol,
                                    'exchange': 'NSE',
                                    'sector': 'Unknown'
                                })
                    
                    # Rate limiting to be respectful
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error fetching batch {batch}: {e}")
                    continue
            
            logger.info(f"Fetched {len(stocks)} stocks from Yahoo Finance")
            return stocks
            
        except Exception as e:
            logger.error(f"Error in Yahoo Finance batch fetch: {e}")
            return []
    
    async def get_comprehensive_stock_list(self) -> List[str]:
        """Get comprehensive list of Indian stock symbols"""
        # Use the comprehensive list from our previous implementation
        comprehensive_symbols = [
            # Nifty 50 + Next 50
            "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
            "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
            "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",
            "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
            "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
            "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LT",
            "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
            "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA",
            "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM",
            "TITAN", "ULTRACEMCO", "UPL", "WIPRO",
            
            # Additional popular stocks
            "ABB", "ACC", "ADANIGREEN", "AUBANK", "BANDHANBNK",
            "BERGEPAINT", "BIOCON", "CANBK", "DABUR", "DMART",
            "FEDERALBNK", "GAIL", "GODREJCP", "HAVELLS", "INDIGO",
            "IOC", "IRCTC", "LICHSGFIN", "LUPIN", "MARICO",
            "MGL", "MPHASIS", "MRF", "NMDC", "PAGEIND",
            "PETRONET", "PFC", "PIDILITIND", "PNB", "RBLBANK",
            "SAIL", "SHREECEM", "SIEMENS", "SRF", "TRENT",
            "TVSMOTOR", "VEDL", "VOLTAS", "YESBANK", "ZEEL",
            
            # Mid and Small Cap
            "DIXON", "CROMPTON", "LALPATHLAB", "METROPOLIS", "ASTRAL",
            "POLYCAB", "VBL", "RADICO", "TRIDENT", "DLF",
            "SOBHA", "BRIGADE", "IRB", "GRANULES", "LAURUSLABS",
            "PERSISTENT", "COFORGE", "LTIM", "HAPPSTMNDS", "ZOMATO",
            "PAYTM", "NYKAA", "POLICYBZR"
        ]
        
        return comprehensive_symbols

class EnhancedStockService:
    """Enhanced stock service with comprehensive features"""
    
    def __init__(self):
        self.fetcher = EnhancedStockDataFetcher()
        self.scheduler = None
    
    async def populate_database_comprehensive(self, db: Session, force_refresh: bool = False) -> int:
        """
        Comprehensive database population using multiple sources
        Following the approach from StockManagement.py
        """
        if not force_refresh:
            existing_count = db.query(Stock).count()
            if existing_count > 200:
                logger.info(f"Database already has {existing_count} stocks. Skipping population.")
                return existing_count
        
        logger.info("🚀 Starting comprehensive stock database population...")
        start_time = time.time()
        
        all_stocks = []
        
        try:
            # Method 1: Try NSE API first
            logger.info("📊 Fetching from NSE API...")
            nse_stocks = await self.fetcher.fetch_nse_api_stocks()
            all_stocks.extend(nse_stocks)
            
            # Method 2: Enhance with Yahoo Finance data
            logger.info("📈 Enhancing with Yahoo Finance data...")
            symbols = await self.fetcher.get_comprehensive_stock_list()
            yf_stocks = await self.fetcher.fetch_yahoo_finance_batch(symbols)
            all_stocks.extend(yf_stocks)
            
        except Exception as e:
            logger.error(f"Error in data fetching: {e}")
        
        # Remove duplicates and merge data
        unique_stocks = {}
        for stock in all_stocks:
            symbol = stock['symbol']
            if symbol in unique_stocks:
                # Merge data, preferring non-null values
                existing = unique_stocks[symbol]
                for key, value in stock.items():
                    if value is not None and (existing.get(key) is None or key == 'last_price'):
                        existing[key] = value
            else:
                unique_stocks[symbol] = stock
        
        logger.info(f"📋 Processing {len(unique_stocks)} unique stocks for database...")
        
        # Insert/update in database
        inserted_count = 0
        updated_count = 0
        
        for symbol, stock_data in unique_stocks.items():
            try:
                existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
                
                if existing_stock:
                    # Update existing stock
                    if stock_data.get('name'):
                        existing_stock.name = stock_data['name']
                    if stock_data.get('last_price'):
                        existing_stock.current_price = stock_data['last_price']
                        existing_stock.previous_close = existing_stock.current_price
                    if stock_data.get('sector'):
                        existing_stock.sector = stock_data['sector']
                    
                    updated_count += 1
                else:
                    # Create new stock
                    new_stock = Stock(
                        symbol=symbol,
                        name=stock_data.get('name', symbol),
                        current_price=stock_data.get('last_price', 100.0),
                        previous_close=stock_data.get('last_price', 100.0),
                        exchange=stock_data.get('exchange', 'NSE'),
                        sector=stock_data.get('sector', 'Unknown'),
                        is_active=True
                    )
                    db.add(new_stock)
                    inserted_count += 1
                
                # Commit in batches
                if (inserted_count + updated_count) % 100 == 0:
                    db.commit()
                    logger.info(f"Processed {inserted_count + updated_count} stocks...")
                
            except Exception as e:
                logger.error(f"Error processing stock {symbol}: {e}")
                db.rollback()
                continue
        
        # Final commit
        try:
            db.commit()
            total_stocks = db.query(Stock).count()
            end_time = time.time()
            
            logger.info("✅ Stock population completed!")
            logger.info(f"📈 New stocks added: {inserted_count}")
            logger.info(f"🔄 Existing stocks updated: {updated_count}")
            logger.info(f"🎯 Total stocks in database: {total_stocks}")
            logger.info(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
            
            return total_stocks
            
        except Exception as e:
            logger.error(f"Final commit error: {e}")
            db.rollback()
            return 0
    
    def search_stocks_advanced(self, db: Session, query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Advanced stock search with pagination (following StockManagement.py approach)
        """
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build search query with fuzzy matching
        search_filter = or_(
            Stock.symbol.ilike(f"%{query}%"),
            Stock.name.ilike(f"%{query}%"),
            Stock.sector.ilike(f"%{query}%")
        )
        
        # Get total count
        total = db.query(Stock).filter(search_filter, Stock.is_active == True).count()
        
        # Get paginated results with ordering
        stocks = db.query(Stock).filter(search_filter, Stock.is_active == True)\
                   .order_by(Stock.symbol)\
                   .offset(offset).limit(per_page).all()
        
        return {
            "stocks": [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "exchange": stock.exchange,
                    "sector": stock.sector,
                    "current_price": stock.current_price,
                    "is_active": stock.is_active
                }
                for stock in stocks
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    def get_database_stats(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            total_stocks = db.query(Stock).count()
            active_stocks = db.query(Stock).filter(Stock.is_active == True).count()
            
            # Exchange breakdown
            exchange_stats = db.query(Stock.exchange, func.count(Stock.id)).group_by(Stock.exchange).all()
            
            # Sector breakdown (top 10)
            sector_stats = db.query(Stock.sector, func.count(Stock.id))\
                            .group_by(Stock.sector)\
                            .order_by(func.count(Stock.id).desc())\
                            .limit(10).all()
            
            # Price statistics
            price_stats = db.query(
                func.min(Stock.current_price),
                func.max(Stock.current_price),
                func.avg(Stock.current_price)
            ).first()
            
            return {
                "total_stocks": total_stocks,
                "active_stocks": active_stocks,
                "exchanges": {exchange: count for exchange, count in exchange_stats},
                "top_sectors": {sector or "Unknown": count for sector, count in sector_stats},
                "price_range": {
                    "min": float(price_stats[0]) if price_stats[0] else 0,
                    "max": float(price_stats[1]) if price_stats[1] else 0,
                    "average": float(price_stats[2]) if price_stats[2] else 0
                },
                "last_updated": datetime.now().isoformat(),
                "status": "healthy" if total_stocks > 100 else "needs_update"
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    def setup_scheduler(self):
        """Setup background scheduler for daily updates"""
        if not SCHEDULER_AVAILABLE:
            logger.warning("⚠️  APScheduler not available - daily updates disabled")
            return
            
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
            
            # Daily update at 1 AM
            self.scheduler.add_job(
                self.daily_stock_update,
                'cron',
                hour=1,
                minute=0,
                id='daily_stock_update'
            )
            
            self.scheduler.start()
            logger.info("📅 Background scheduler started for daily updates")
    
    async def daily_stock_update(self):
        """Background task for daily stock updates"""
        if not SCHEDULER_AVAILABLE:
            logger.warning("⚠️  Scheduler not available for daily updates")
            return
            
        logger.info("🌅 Starting daily stock update...")
        
        db = SessionLocal()
        try:
            updated_count = await self.populate_database_comprehensive(db, force_refresh=True)
            logger.info(f"✅ Daily update complete. Database has {updated_count} stocks.")
        except Exception as e:
            logger.error(f"❌ Daily update failed: {e}")
        finally:
            db.close()

# Global service instance
enhanced_stock_service = EnhancedStockService()

# FastAPI startup functions
async def enhanced_startup_population():
    """Enhanced startup stock population"""
    logger.info("🌟 Enhanced FastAPI startup: Initializing comprehensive stock database...")
    
    db = SessionLocal()
    try:
        stock_count = await enhanced_stock_service.populate_database_comprehensive(db)
        enhanced_stock_service.setup_scheduler()
        logger.info(f"🎉 Enhanced startup complete! Database has {stock_count} stocks with daily updates scheduled.")
        return stock_count
    except Exception as e:
        logger.error(f"❌ Enhanced startup failed: {e}")
        return 0
    finally:
        db.close()

# Export functions for use in main FastAPI app
__all__ = [
    'enhanced_stock_service',
    'enhanced_startup_population',
    'EnhancedStockService',
    'EnhancedStockDataFetcher'
]
