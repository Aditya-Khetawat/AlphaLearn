"""
Automated script to seed the database with ALL Indian stocks from NSE and BSE

This script automatically fetches comprehensive stock lists from:
1. NSE Official API (free, no authentication)
2. Yahoo Finance Screener (free)
3. Web scraping as fallback

Usage: python seed_stocks.py
"""

import sys
import os
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Set
import logging

# Add the parent directory to sys.path to allow imports from the app
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock_data import StockDataService
from app.models.models import Stock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedStockFetcher:
    """
    Automatically fetch all Indian stocks from multiple free sources
    """
    
    def __init__(self):
        self.session = requests.Session()
        # Set headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def fetch_nse_stocks(self) -> Set[Dict[str, str]]:
        """
        Fetch all NSE stocks from NSE's official free API
        """
        logger.info("Fetching stocks from NSE official API...")
        stock_set = set()
        
        try:
            # NSE indices that contain comprehensive stock lists
            indices = [
                'NIFTY%20500',
                'NIFTY%20TOTAL%20MARKET',
                'NIFTY%20SMALLCAP%20100',
                'NIFTY%20MIDCAP%20100',
                'NIFTY%20LARGEMIDCAP%20250'
            ]
            
            for index in indices:
                try:
                    url = f'https://www.nseindia.com/api/equity-stockIndices?index={index}'
                    logger.info(f"Fetching from: {index.replace('%20', ' ')}")
                    
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'data' in data:
                            for stock in data['data']:
                                if 'symbol' in stock and 'companyName' in stock:
                                    # Add to set to avoid duplicates
                                    stock_info = (
                                        stock['symbol'],
                                        stock['companyName'],
                                        'NSE'
                                    )
                                    stock_set.add(stock_info)
                    
                    # Be respectful to the API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error fetching {index}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching NSE stocks: {e}")
        
        logger.info(f"Fetched {len(stock_set)} stocks from NSE")
        return stock_set
    
    def fetch_yahoo_finance_indian_stocks(self) -> Set[Dict[str, str]]:
        """
        Fetch Indian stocks from Yahoo Finance screener
        """
        logger.info("Fetching stocks from Yahoo Finance screener...")
        stock_set = set()
        
        try:
            # Yahoo Finance screener for Indian markets
            screener_urls = [
                'https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&lang=en-US&region=US&queryId=most_actives&count=1000',
                'https://query2.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&lang=en-US&region=IN&queryId=most_actives&count=1000'
            ]
            
            for url in screener_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'finance' in data and 'result' in data['finance']:
                            results = data['finance']['result']
                            if results and len(results) > 0 and 'quotes' in results[0]:
                                for quote in results[0]['quotes']:
                                    symbol = quote.get('symbol', '')
                                    name = quote.get('longName', quote.get('shortName', ''))
                                    
                                    # Filter for Indian stocks (.NS or .BO suffix)
                                    if '.NS' in symbol or '.BO' in symbol:
                                        exchange = 'NSE' if '.NS' in symbol else 'BSE'
                                        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                                        
                                        stock_info = (clean_symbol, name, exchange)
                                        stock_set.add(stock_info)
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error fetching from Yahoo screener: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance stocks: {e}")
        
        logger.info(f"Fetched {len(stock_set)} stocks from Yahoo Finance")
        return stock_set
    
    def fetch_popular_indian_stocks(self) -> Set[Dict[str, str]]:
        """
        Fallback list of popular Indian stocks
        """
        logger.info("Using fallback list of popular Indian stocks...")
        
        popular_stocks = [
            ("RELIANCE", "Reliance Industries Ltd", "NSE"),
            ("TCS", "Tata Consultancy Services Ltd", "NSE"),
            ("HDFCBANK", "HDFC Bank Ltd", "NSE"),
            ("INFY", "Infosys Ltd", "NSE"),
            ("SBIN", "State Bank of India", "NSE"),
            ("ICICIBANK", "ICICI Bank Ltd", "NSE"),
            ("HINDUNILVR", "Hindustan Unilever Ltd", "NSE"),
            ("BAJFINANCE", "Bajaj Finance Ltd", "NSE"),
            ("BHARTIARTL", "Bharti Airtel Ltd", "NSE"),
            ("WIPRO", "Wipro Ltd", "NSE"),
            ("AXISBANK", "Axis Bank Ltd", "NSE"),
            ("ITC", "ITC Ltd", "NSE"),
            ("KOTAKBANK", "Kotak Mahindra Bank Ltd", "NSE"),
            ("LT", "Larsen & Toubro Ltd", "NSE"),
            ("ASIANPAINT", "Asian Paints Ltd", "NSE"),
            ("MARUTI", "Maruti Suzuki India Ltd", "NSE"),
            ("TATASTEEL", "Tata Steel Ltd", "NSE"),
            ("TATAMOTORS", "Tata Motors Ltd", "NSE"),
            ("ADANIENT", "Adani Enterprises Ltd", "NSE"),
            ("BAJAJ-AUTO", "Bajaj Auto Ltd", "NSE"),
            ("CIPLA", "Cipla Ltd", "NSE"),
            ("DRREDDY", "Dr. Reddy's Laboratories Ltd", "NSE"),
            ("EICHERMOT", "Eicher Motors Ltd", "NSE"),
            ("GRASIM", "Grasim Industries Ltd", "NSE"),
            ("HCLTECH", "HCL Technologies Ltd", "NSE"),
            ("HEROMOTOCO", "Hero MotoCorp Ltd", "NSE"),
            ("HINDALCO", "Hindalco Industries Ltd", "NSE"),
            ("INDUSINDBK", "IndusInd Bank Ltd", "NSE"),
            ("JSWSTEEL", "JSW Steel Ltd", "NSE"),
            ("M&M", "Mahindra & Mahindra Ltd", "NSE"),
            ("NESTLEIND", "Nestle India Ltd", "NSE"),
            ("NTPC", "NTPC Ltd", "NSE"),
            ("ONGC", "Oil and Natural Gas Corporation Ltd", "NSE"),
            ("POWERGRID", "Power Grid Corporation of India Ltd", "NSE"),
            ("SUNPHARMA", "Sun Pharmaceutical Industries Ltd", "NSE"),
            ("TATACONSUM", "Tata Consumer Products Ltd", "NSE"),
            ("TECHM", "Tech Mahindra Ltd", "NSE"),
            ("TITAN", "Titan Company Ltd", "NSE"),
            ("ULTRACEMCO", "UltraTech Cement Ltd", "NSE"),
            ("UPL", "UPL Ltd", "NSE"),
        ]
        
        return set(popular_stocks)
    
    def get_all_stocks(self) -> List[Dict[str, str]]:
        """
        Get comprehensive list of Indian stocks from all sources
        """
        logger.info("Starting comprehensive stock data collection...")
        all_stocks = set()
        
        # Try multiple sources
        try:
            # Source 1: NSE Official API
            nse_stocks = self.fetch_nse_stocks()
            all_stocks.update(nse_stocks)
        except Exception as e:
            logger.error(f"NSE fetch failed: {e}")
        
        try:
            # Source 2: Yahoo Finance
            yahoo_stocks = self.fetch_yahoo_finance_indian_stocks()
            all_stocks.update(yahoo_stocks)
        except Exception as e:
            logger.error(f"Yahoo Finance fetch failed: {e}")
        
        # Source 3: Fallback popular stocks
        if len(all_stocks) < 50:  # If we don't have enough stocks
            logger.warning("Low stock count, adding popular stocks as fallback")
            popular_stocks = self.fetch_popular_indian_stocks()
            all_stocks.update(popular_stocks)
        
        # Convert to list of dictionaries
        stock_list = []
        for symbol, name, exchange in all_stocks:
            stock_list.append({
                'symbol': symbol,
                'name': name,
                'exchange': exchange
            })
        
        logger.info(f"Total unique stocks collected: {len(stock_list)}")
        return stock_list

def seed_stocks():
    """Automatically seed the database with comprehensive Indian stock data"""
    # Get a database session
    db = next(get_db())
    
    try:
        # Initialize the automated stock fetcher
        fetcher = AutomatedStockFetcher()
        
        # Get comprehensive stock list from multiple sources
        logger.info("Fetching comprehensive stock data from multiple sources...")
        all_stocks = fetcher.get_all_stocks()
        
        if not all_stocks:
            logger.error("No stocks fetched from any source!")
            return
        
        logger.info(f"Found {len(all_stocks)} stocks from all sources")
        
        # Check which stocks already exist
        existing_symbols = {stock.symbol for stock in db.query(Stock).all()}
        new_stocks = [stock for stock in all_stocks if stock['symbol'] not in existing_symbols]
        
        if not new_stocks:
            logger.info("All fetched stocks already exist in the database.")
            return
        
        logger.info(f"Adding {len(new_stocks)} new stocks to database...")
        
        # Process stocks in batches to avoid overwhelming Yahoo Finance
        batch_size = 20
        successful_additions = 0
        
        for i in range(0, len(new_stocks), batch_size):
            batch = new_stocks[i:i + batch_size]
            batch_symbols = [stock['symbol'] for stock in batch]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(new_stocks)-1)//batch_size + 1} ({len(batch)} stocks)")
            
            try:
                # Get detailed stock data from Yahoo Finance
                stock_data_list = StockDataService.get_multiple_stocks(batch_symbols)
                
                # Create a lookup for detailed data
                detailed_data = {data['symbol']: data for data in stock_data_list}
                
                # Add stocks to database
                for stock_info in batch:
                    symbol = stock_info['symbol']
                    try:
                        # Use detailed data if available, otherwise use basic info
                        if symbol in detailed_data:
                            data = detailed_data[symbol]
                            stock = Stock(
                                symbol=symbol,
                                name=data["name"],
                                current_price=data["current_price"],
                                previous_close=data["previous_close"],
                                exchange=stock_info['exchange'],
                                is_active=True,
                                last_updated=data["updated_at"]
                            )
                        else:
                            # Use basic info with default price
                            stock = Stock(
                                symbol=symbol,
                                name=stock_info["name"],
                                current_price=100.0,  # Default price
                                previous_close=100.0,
                                exchange=stock_info['exchange'],
                                is_active=True
                            )
                        
                        db.add(stock)
                        successful_additions += 1
                        logger.info(f"Added stock: {symbol} ({stock.name})")
                        
                    except Exception as e:
                        logger.error(f"Error adding stock {symbol}: {e}")
                        continue
                
                # Commit this batch
                db.commit()
                logger.info(f"Committed batch {i//batch_size + 1}")
                
                # Be respectful to APIs
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing batch starting at {i}: {e}")
                db.rollback()
                continue
        
        logger.info(f"Database seeding completed! Successfully added {successful_additions} stocks.")
        
        # Final count
        total_stocks = db.query(Stock).count()
        logger.info(f"Total stocks in database: {total_stocks}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_stocks()
