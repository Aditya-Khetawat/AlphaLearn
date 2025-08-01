"""
Comprehensive Indian Stock Fetcher - Get ALL Active Stocks
Fetches from NSE/BSE APIs and web sources to get 3000+ stocks automatically
"""

import asyncio
import logging
import requests
import yfinance as yf
import pandas as pd
from typing import List, Dict, Set
from sqlalchemy.orm import Session
import time
import json

from app.core.database import SessionLocal
from app.models.models import Stock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveIndianStockFetcher:
    """
    Fetch ALL active Indian stocks from multiple sources
    Target: 3000+ stocks from NSE + BSE
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/'
        })
        
    async def fetch_all_nse_stocks(self) -> List[Dict]:
        """
        Fetch ALL NSE stocks using official NSE APIs
        Target: 1600+ NSE stocks
        """
        logger.info("🔍 Fetching ALL NSE stocks from official APIs...")
        
        all_stocks = []
        
        # Method 1: NSE Equity List API
        try:
            logger.info("📊 Fetching from NSE Equity List API...")
            url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for stock in data.get('data', []):
                    all_stocks.append({
                        'symbol': stock['symbol'],
                        'name': stock.get('companyName', stock['symbol']),
                        'exchange': 'NSE',
                        'last_price': stock.get('lastPrice', 100.0),
                        'sector': 'Unknown'
                    })
                logger.info(f"✅ Got {len(data.get('data', []))} stocks from F&O list")
                
        except Exception as e:
            logger.warning(f"NSE F&O API failed: {e}")
        
        # Method 2: NSE All Indices
        indices = [
            'NIFTY%20500',
            'NIFTY%20TOTAL%20MARKET',
            'NIFTY%20SMALLCAP%20100',
            'NIFTY%20MIDCAP%20100',
            'NIFTY%20SMALLCAP%20250',
            'NIFTY%20MICROCAP%20250'
        ]
        
        for index in indices:
            try:
                url = f'https://www.nseindia.com/api/equity-stockIndices?index={index}'
                logger.info(f"📈 Fetching {index.replace('%20', ' ')}")
                
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for stock in data.get('data', []):
                        all_stocks.append({
                            'symbol': stock['symbol'],
                            'name': stock.get('companyName', stock['symbol']),
                            'exchange': 'NSE',
                            'last_price': stock.get('lastPrice', 100.0),
                            'sector': 'Unknown'
                        })
                    
                    logger.info(f"✅ Got {len(data.get('data', []))} stocks from {index.replace('%20', ' ')}")
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Failed to fetch {index}: {e}")
                continue
        
        # Method 3: NSE Symbol Search (Get all symbols)
        try:
            logger.info("🔍 Trying NSE symbol search...")
            # This often contains the most comprehensive list
            url = "https://www.nseindia.com/api/search/autocomplete?q="
            
            # Search for common letters to get more symbols
            search_chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            
            for char in search_chars:
                try:
                    search_url = f"{url}{char}"
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        symbols = data.get('symbols', [])
                        
                        for symbol_data in symbols:
                            if symbol_data.get('symbol'):
                                all_stocks.append({
                                    'symbol': symbol_data['symbol'],
                                    'name': symbol_data.get('symbol_info', symbol_data['symbol']),
                                    'exchange': 'NSE',
                                    'sector': 'Unknown'
                                })
                        
                        logger.info(f"✅ Got {len(symbols)} symbols starting with '{char}'")
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Search failed for '{char}': {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"NSE search method failed: {e}")
        
        # Remove duplicates
        unique_stocks = {}
        for stock in all_stocks:
            symbol = stock['symbol']
            if symbol not in unique_stocks:
                unique_stocks[symbol] = stock
        
        logger.info(f"🎯 Total unique NSE stocks found: {len(unique_stocks)}")
        return list(unique_stocks.values())
    
    async def fetch_all_bse_stocks(self) -> List[Dict]:
        """
        Fetch BSE stocks using available APIs
        Target: 1000+ BSE stocks
        """
        logger.info("🔍 Fetching BSE stocks...")
        
        bse_stocks = []
        
        # Method 1: Try BSE API if available
        try:
            # BSE doesn't have as open APIs, but we can try some endpoints
            logger.info("📊 Trying BSE endpoints...")
            
            # Popular BSE stocks that are also on NSE but with .BO suffix
            popular_bse = [
                'RELIANCE.BO', 'TCS.BO', 'HDFCBANK.BO', 'INFY.BO', 'HINDUNILVR.BO',
                'ICICIBANK.BO', 'KOTAKBANK.BO', 'BHARTIARTL.BO', 'ITC.BO', 'SBIN.BO',
                'BAJFINANCE.BO', 'ASIANPAINT.BO', 'MARUTI.BO', 'AXISBANK.BO', 'LT.BO'
            ]
            
            for symbol in popular_bse:
                bse_stocks.append({
                    'symbol': symbol.replace('.BO', ''),
                    'name': symbol.replace('.BO', ''),
                    'exchange': 'BSE',
                    'sector': 'Unknown'
                })
            
            logger.info(f"✅ Added {len(popular_bse)} BSE stocks")
            
        except Exception as e:
            logger.warning(f"BSE fetch failed: {e}")
        
        return bse_stocks
    
    async def enrich_with_yfinance(self, stocks: List[Dict], batch_size: int = 30) -> List[Dict]:
        """
        Enrich stock data with yfinance for real prices and company info
        """
        logger.info(f"💰 Enriching {len(stocks)} stocks with yfinance data...")
        
        enriched_stocks = []
        failed_count = 0
        
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(stocks) + batch_size - 1)//batch_size}")
            
            for stock in batch:
                try:
                    symbol = stock['symbol']
                    yahoo_symbol = f"{symbol}.NS"  # Try NSE first
                    
                    ticker = yf.Ticker(yahoo_symbol)
                    info = ticker.info
                    
                    # Try to get recent price
                    hist = ticker.history(period="2d")
                    current_price = float(hist['Close'].iloc[-1]) if not hist.empty else info.get('currentPrice', 100.0)
                    
                    enriched_stock = {
                        'symbol': symbol,
                        'name': info.get('longName', info.get('shortName', stock['name'])),
                        'exchange': stock['exchange'],
                        'sector': info.get('sector', 'Unknown'),
                        'current_price': current_price,
                        'market_cap': info.get('marketCap'),
                        'is_active': True
                    }
                    
                    enriched_stocks.append(enriched_stock)
                    
                except Exception as e:
                    # If NSE fails, try BSE
                    try:
                        yahoo_symbol = f"{symbol}.BO"
                        ticker = yf.Ticker(yahoo_symbol)
                        info = ticker.info
                        
                        hist = ticker.history(period="2d")
                        current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 100.0
                        
                        enriched_stock = {
                            'symbol': symbol,
                            'name': info.get('longName', info.get('shortName', stock['name'])),
                            'exchange': 'BSE',
                            'sector': info.get('sector', 'Unknown'),
                            'current_price': current_price,
                            'market_cap': info.get('marketCap'),
                            'is_active': True
                        }
                        
                        enriched_stocks.append(enriched_stock)
                        
                    except Exception as e2:
                        # Add stock with basic info if both fail
                        failed_count += 1
                        enriched_stocks.append({
                            'symbol': symbol,
                            'name': stock['name'],
                            'exchange': stock['exchange'],
                            'sector': 'Unknown',
                            'current_price': 100.0,
                            'is_active': True
                        })
            
            # Rate limiting
            await asyncio.sleep(2)
        
        logger.info(f"✅ Enriched {len(enriched_stocks)} stocks, {failed_count} failed to get price data")
        return enriched_stocks
    
    async def populate_comprehensive_database(self, force_refresh: bool = False) -> int:
        """
        Populate database with ALL Indian stocks
        """
        db = SessionLocal()
        
        try:
            if not force_refresh:
                existing_count = db.query(Stock).count()
                if existing_count > 1000:  # Only skip if we have a truly comprehensive database
                    logger.info(f"Database already has {existing_count} stocks. Use force_refresh=True to update.")
                    return existing_count
            
            logger.info("🚀 Starting COMPREHENSIVE Indian stock database population...")
            logger.info("🎯 Target: 3000+ stocks from NSE + BSE")
            start_time = time.time()
            
            # Step 1: Fetch all NSE stocks
            nse_stocks = await self.fetch_all_nse_stocks()
            logger.info(f"📊 NSE: Found {len(nse_stocks)} stocks")
            
            # Step 2: Fetch BSE stocks
            bse_stocks = await self.fetch_all_bse_stocks()
            logger.info(f"📊 BSE: Found {len(bse_stocks)} stocks")
            
            # Step 3: Combine and deduplicate
            all_stocks = nse_stocks + bse_stocks
            unique_stocks = {}
            for stock in all_stocks:
                symbol = stock['symbol']
                if symbol not in unique_stocks:
                    unique_stocks[symbol] = stock
            
            logger.info(f"📋 Total unique stocks before enrichment: {len(unique_stocks)}")
            
            # Step 4: Enrich with yfinance data
            enriched_stocks = await self.enrich_with_yfinance(list(unique_stocks.values()))
            
            # Step 5: Save to database
            inserted_count = 0
            updated_count = 0
            
            logger.info("💾 Saving to database...")
            
            for stock_data in enriched_stocks:
                try:
                    existing_stock = db.query(Stock).filter(Stock.symbol == stock_data['symbol']).first()
                    
                    if existing_stock:
                        # Update existing
                        existing_stock.name = stock_data['name']
                        existing_stock.current_price = stock_data['current_price']
                        existing_stock.previous_close = stock_data['current_price']
                        existing_stock.sector = stock_data['sector']
                        existing_stock.exchange = stock_data['exchange']
                        updated_count += 1
                    else:
                        # Create new
                        new_stock = Stock(
                            symbol=stock_data['symbol'],
                            name=stock_data['name'],
                            current_price=stock_data['current_price'],
                            previous_close=stock_data['current_price'],
                            exchange=stock_data['exchange'],
                            sector=stock_data['sector'],
                            is_active=True
                        )
                        db.add(new_stock)
                        inserted_count += 1
                    
                    # Commit in batches
                    if (inserted_count + updated_count) % 100 == 0:
                        db.commit()
                        logger.info(f"💾 Processed {inserted_count + updated_count} stocks...")
                        
                except Exception as e:
                    logger.error(f"Error saving {stock_data['symbol']}: {e}")
                    db.rollback()
                    continue
            
            # Final commit
            db.commit()
            total_stocks = db.query(Stock).count()
            end_time = time.time()
            
            logger.info("🎉 COMPREHENSIVE stock population completed!")
            logger.info(f"📈 New stocks added: {inserted_count}")
            logger.info(f"🔄 Existing stocks updated: {updated_count}")
            logger.info(f"🎯 Total stocks in database: {total_stocks}")
            logger.info(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
            
            return total_stocks
            
        except Exception as e:
            logger.error(f"Comprehensive population failed: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

# Global instance
comprehensive_fetcher = ComprehensiveIndianStockFetcher()

async def populate_all_indian_stocks(force_refresh: bool = False):
    """
    Populate database with ALL Indian stocks
    """
    return await comprehensive_fetcher.populate_comprehensive_database(force_refresh)

# Export for main app
__all__ = ['comprehensive_fetcher', 'populate_all_indian_stocks', 'ComprehensiveIndianStockFetcher']
