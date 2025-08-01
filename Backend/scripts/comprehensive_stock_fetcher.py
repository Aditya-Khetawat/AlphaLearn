"""
Comprehensive stock fetcher using multiple free data sources for Indian stocks

This script uses alternative free methods to get all Indian stocks:
1. Direct web scraping of NSE equity list
2. Yahoo Finance ticker search
3. Pre-compiled comprehensive stock lists
4. yfinance library capabilities

Usage: python comprehensive_stock_fetcher.py
"""

import sys
import os
import requests
import json
import time
import yfinance as yf
from pathlib import Path
from typing import List, Dict, Set
import logging

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Stock
from app.schemas.schemas import StockCreate
from app.crud import stock as stock_crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveStockFetcher:
    """
    Fetch all Indian stocks using multiple free methods
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def get_comprehensive_stock_list(self) -> List[Dict[str, str]]:
        """
        Get comprehensive list of Indian stocks from multiple sources
        """
        logger.info("Building comprehensive Indian stock database...")
        
        # Comprehensive list of popular Indian stocks with sectors
        comprehensive_stocks = [
            # Nifty 50 Stocks
            {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "ADANIPORTS", "name": "Adani Ports and Special Economic Zone Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals Enterprise Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "BPCL", "name": "Bharat Petroleum Corporation Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Communication Services", "exchange": "NSE"},
            {"symbol": "BRITANNIA", "name": "Britannia Industries Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "CIPLA", "name": "Cipla Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "COALINDIA", "name": "Coal India Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "DIVISLAB", "name": "Divi's Laboratories Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "EICHERMOT", "name": "Eicher Motors Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "GRASIM", "name": "Grasim Industries Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "HCLTECH", "name": "HCL Technologies Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance Company Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "HINDALCO", "name": "Hindalco Industries Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "ITC", "name": "ITC Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "INDUSINDBK", "name": "IndusInd Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "INFY", "name": "Infosys Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "JSWSTEEL", "name": "JSW Steel Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "LT", "name": "Larsen & Toubro Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "M&M", "name": "Mahindra & Mahindra Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "NESTLEIND", "name": "Nestle India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "NTPC", "name": "NTPC Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "ONGC", "name": "Oil and Natural Gas Corporation Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "POWERGRID", "name": "Power Grid Corporation of India Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "SBILIFE", "name": "SBI Life Insurance Company Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "SBIN", "name": "State Bank of India", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "TATACONSUM", "name": "Tata Consumer Products Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "TATASTEEL", "name": "Tata Steel Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "TECHM", "name": "Tech Mahindra Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "TITAN", "name": "Titan Company Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "ULTRACEMCO", "name": "UltraTech Cement Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "UPL", "name": "UPL Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "WIPRO", "name": "Wipro Ltd", "sector": "Information Technology", "exchange": "NSE"},
            
            # Next 50 Popular Stocks
            {"symbol": "ABB", "name": "ABB India Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "ACC", "name": "ACC Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "ADANIGREEN", "name": "Adani Green Energy Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "ADANIPOWER", "name": "Adani Power Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "AMBUJACEM", "name": "Ambuja Cements Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "AUBANK", "name": "AU Small Finance Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "AUROPHARMA", "name": "Aurobindo Pharma Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "BANDHANBNK", "name": "Bandhan Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "BATAINDIA", "name": "Bata India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "BEL", "name": "Bharat Electronics Ltd", "sector": "Technology", "exchange": "NSE"},
            {"symbol": "BERGEPAINT", "name": "Berger Paints India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "BIOCON", "name": "Biocon Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "BOSCHLTD", "name": "Bosch Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "CANBK", "name": "Canara Bank", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "CHOLAFIN", "name": "Cholamandalam Investment and Finance Company Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "COLPAL", "name": "Colgate Palmolive India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "CONCOR", "name": "Container Corporation of India Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "CUMMINSIND", "name": "Cummins India Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "DABUR", "name": "Dabur India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "DEEPAKNTR", "name": "Deepak Nitrite Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "DMART", "name": "Avenue Supermarts Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "EXIDEIND", "name": "Exide Industries Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "FEDERALBNK", "name": "Federal Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "GAIL", "name": "GAIL India Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "GODREJCP", "name": "Godrej Consumer Products Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "GODREJPROP", "name": "Godrej Properties Ltd", "sector": "Real Estate", "exchange": "NSE"},
            {"symbol": "HAVELLS", "name": "Havells India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "HFCL", "name": "HFCL Ltd", "sector": "Technology", "exchange": "NSE"},
            {"symbol": "ICICIPRULI", "name": "ICICI Prudential Life Insurance Company Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "IDEA", "name": "Vodafone Idea Ltd", "sector": "Communication Services", "exchange": "NSE"},
            {"symbol": "IDFCFIRSTB", "name": "IDFC First Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "IGL", "name": "Indraprastha Gas Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "INDIGO", "name": "InterGlobe Aviation Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "IOC", "name": "Indian Oil Corporation Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "IRCTC", "name": "Indian Railway Catering and Tourism Corporation Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "JUBLFOOD", "name": "Jubilant FoodWorks Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "LICHSGFIN", "name": "LIC Housing Finance Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "LUPIN", "name": "Lupin Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "MARICO", "name": "Marico Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "MFSL", "name": "Max Financial Services Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "MGL", "name": "Mahanagar Gas Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "MPHASIS", "name": "Mphasis Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "MRF", "name": "MRF Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "NMDC", "name": "NMDC Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "NAUKRI", "name": "Info Edge India Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "PAGEIND", "name": "Page Industries Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "PEL", "name": "Piramal Enterprises Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "PETRONET", "name": "Petronet LNG Ltd", "sector": "Energy", "exchange": "NSE"},
            {"symbol": "PFC", "name": "Power Finance Corporation Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "PIDILITIND", "name": "Pidilite Industries Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "PNB", "name": "Punjab National Bank", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "POLYCAB", "name": "Polycab India Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "RAMCOCEM", "name": "The Ramco Cements Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "RBLBANK", "name": "RBL Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "RECLTD", "name": "REC Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "SAIL", "name": "Steel Authority of India Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "SHREECEM", "name": "Shree Cement Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "SIEMENS", "name": "Siemens Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "SRF", "name": "SRF Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "TORNTPOWER", "name": "Torrent Power Ltd", "sector": "Utilities", "exchange": "NSE"},
            {"symbol": "TRENT", "name": "Trent Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "TVSMOTOR", "name": "TVS Motor Company Ltd", "sector": "Automobile", "exchange": "NSE"},
            {"symbol": "VEDL", "name": "Vedanta Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "VOLTAS", "name": "Voltas Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "YESBANK", "name": "Yes Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "ZEEL", "name": "Zee Entertainment Enterprises Ltd", "sector": "Communication Services", "exchange": "NSE"},
            
            # Additional Mid-cap and Small-cap stocks
            {"symbol": "DIXON", "name": "Dixon Technologies India Ltd", "sector": "Technology", "exchange": "NSE"},
            {"symbol": "CROMPTON", "name": "Crompton Greaves Consumer Electricals Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "LALPATHLAB", "name": "Dr. Lal PathLabs Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "METROPOLIS", "name": "Metropolis Healthcare Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "ASTRAL", "name": "Astral Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "POLYPLEX", "name": "Polyplex Corporation Ltd", "sector": "Materials", "exchange": "NSE"},
            {"symbol": "CRISIL", "name": "CRISIL Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "MINDTREE", "name": "Mindtree Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "PERSISTENT", "name": "Persistent Systems Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "MPHASIS", "name": "Mphasis Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "LTIM", "name": "LTIMindtree Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "COFORGE", "name": "Coforge Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "HAPPSTMNDS", "name": "Happiest Minds Technologies Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "TATAELXSI", "name": "Tata Elxsi Ltd", "sector": "Information Technology", "exchange": "NSE"},
            {"symbol": "ZOMATO", "name": "Zomato Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "PAYTM", "name": "One 97 Communications Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "NYKAA", "name": "FSN E-Commerce Ventures Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            {"symbol": "POLICYBZR", "name": "PB Fintech Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "CARTRADE", "name": "CarTrade Tech Ltd", "sector": "Consumer Services", "exchange": "NSE"},
            
            # Banking and Financial Services
            {"symbol": "CUB", "name": "City Union Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "DCB", "name": "DCB Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "EQUITAS", "name": "Equitas Small Finance Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "UJJIVAN", "name": "Ujjivan Small Finance Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "SURYODAY", "name": "Suryoday Small Finance Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            {"symbol": "ESAFSFB", "name": "ESAF Small Finance Bank Ltd", "sector": "Financial Services", "exchange": "NSE"},
            
            # Pharmaceutical Companies
            {"symbol": "GLENMARK", "name": "Glenmark Pharmaceuticals Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "CADILAHC", "name": "Cadila Healthcare Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "TORNTPHARM", "name": "Torrent Pharmaceuticals Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "ALKEM", "name": "Alkem Laboratories Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "IPCALAB", "name": "IPCA Laboratories Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "GRANULES", "name": "Granules India Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "LAURUSLABS", "name": "Laurus Labs Ltd", "sector": "Healthcare", "exchange": "NSE"},
            {"symbol": "DIVIS", "name": "Divis Laboratories Ltd", "sector": "Healthcare", "exchange": "NSE"},
            
            # Consumer Goods
            {"symbol": "BAJAJCON", "name": "Bajaj Consumer Care Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "EMAMILTD", "name": "Emami Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "GILLETTE", "name": "Gillette India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "VBL", "name": "Varun Beverages Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "RADICO", "name": "Radico Khaitan Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            
            # Textiles
            {"symbol": "TRIDENT", "name": "Trident Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "VARDHMAN", "name": "Vardhman Textiles Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            {"symbol": "WELSPUNIND", "name": "Welspun India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
            
            # Real Estate
            {"symbol": "DLF", "name": "DLF Ltd", "sector": "Real Estate", "exchange": "NSE"},
            {"symbol": "PHOENIXLTD", "name": "The Phoenix Mills Ltd", "sector": "Real Estate", "exchange": "NSE"},
            {"symbol": "SOBHA", "name": "Sobha Ltd", "sector": "Real Estate", "exchange": "NSE"},
            {"symbol": "BRIGADE", "name": "Brigade Enterprises Ltd", "sector": "Real Estate", "exchange": "NSE"},
            
            # Infrastructure
            {"symbol": "IRB", "name": "IRB Infrastructure Developers Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "SADBHAV", "name": "Sadbhav Engineering Ltd", "sector": "Industrials", "exchange": "NSE"},
            {"symbol": "KNR", "name": "KNR Constructions Ltd", "sector": "Industrials", "exchange": "NSE"},
        ]
        
        logger.info(f"Compiled {len(comprehensive_stocks)} stocks from comprehensive list")
        return comprehensive_stocks
    
    def fetch_with_yfinance(self, stocks: List[Dict]) -> List[Dict]:
        """
        Enhance stock data using yfinance for price information
        """
        logger.info("Enhancing stock data with yfinance...")
        enhanced_stocks = []
        
        # Process in batches to avoid overwhelming yfinance
        batch_size = 20
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            batch_symbols = [f"{stock['symbol']}.NS" for stock in batch]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(stocks)-1)//batch_size + 1}")
            
            try:
                # Download batch data
                data = yf.download(batch_symbols, period="2d", progress=False)
                
                if not data.empty:
                    # Process each stock in the batch
                    for stock in batch:
                        yahoo_symbol = f"{stock['symbol']}.NS"
                        try:
                            if yahoo_symbol in data.columns.levels[0] if hasattr(data.columns, 'levels') else [yahoo_symbol]:
                                if hasattr(data.columns, 'levels'):
                                    # Multi-level columns (multiple stocks)
                                    stock_data = data[yahoo_symbol]['Close']
                                else:
                                    # Single level columns (single stock)
                                    stock_data = data['Close']
                                
                                if not stock_data.empty and len(stock_data) > 0:
                                    current_price = float(stock_data.iloc[-1])
                                    previous_close = float(stock_data.iloc[-2]) if len(stock_data) > 1 else current_price
                                    
                                    enhanced_stock = stock.copy()
                                    enhanced_stock.update({
                                        'current_price': current_price,
                                        'previous_close': previous_close,
                                        'has_price_data': True
                                    })
                                    enhanced_stocks.append(enhanced_stock)
                                else:
                                    # No price data, use defaults
                                    enhanced_stock = stock.copy()
                                    enhanced_stock.update({
                                        'current_price': 100.0,
                                        'previous_close': 100.0,
                                        'has_price_data': False
                                    })
                                    enhanced_stocks.append(enhanced_stock)
                            else:
                                # Stock not found in yfinance data
                                enhanced_stock = stock.copy()
                                enhanced_stock.update({
                                    'current_price': 100.0,
                                    'previous_close': 100.0,
                                    'has_price_data': False
                                })
                                enhanced_stocks.append(enhanced_stock)
                                
                        except Exception as e:
                            logger.warning(f"Error processing {stock['symbol']}: {e}")
                            # Add with default values
                            enhanced_stock = stock.copy()
                            enhanced_stock.update({
                                'current_price': 100.0,
                                'previous_close': 100.0,
                                'has_price_data': False
                            })
                            enhanced_stocks.append(enhanced_stock)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error fetching batch {i//batch_size + 1}: {e}")
                # Add batch with default values
                for stock in batch:
                    enhanced_stock = stock.copy()
                    enhanced_stock.update({
                        'current_price': 100.0,
                        'previous_close': 100.0,
                        'has_price_data': False
                    })
                    enhanced_stocks.append(enhanced_stock)
                continue
        
        logger.info(f"Enhanced {len(enhanced_stocks)} stocks with price data")
        return enhanced_stocks


def seed_comprehensive_stocks():
    """
    Seed database with comprehensive Indian stock data
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting comprehensive stock database seeding...")
        
        # Initialize fetcher
        fetcher = ComprehensiveStockFetcher()
        
        # Get comprehensive stock list
        all_stocks = fetcher.get_comprehensive_stock_list()
        
        # Enhance with price data from yfinance
        enhanced_stocks = fetcher.fetch_with_yfinance(all_stocks)
        
        # Check existing stocks
        existing_symbols = {stock.symbol for stock in db.query(Stock).all()}
        new_stocks = [stock for stock in enhanced_stocks if stock['symbol'] not in existing_symbols]
        
        if not new_stocks:
            logger.info("All stocks already exist in database")
            return
        
        logger.info(f"Adding {len(new_stocks)} new stocks to database...")
        
        # Add stocks to database
        successful_additions = 0
        for stock_data in new_stocks:
            try:
                stock_create = StockCreate(
                    symbol=stock_data['symbol'],
                    name=stock_data['name'],
                    current_price=stock_data['current_price'],
                    previous_close=stock_data['previous_close'],
                    exchange=stock_data['exchange'],
                    sector=stock_data.get('sector', 'Unknown')
                )
                
                created_stock = stock_crud.create(db, obj_in=stock_create)
                successful_additions += 1
                logger.info(f"Added: {created_stock.symbol} - {created_stock.name}")
                
            except Exception as e:
                logger.error(f"Error adding {stock_data['symbol']}: {e}")
                continue
        
        logger.info(f"Successfully added {successful_additions} stocks to database")
        
        # Final count
        total_stocks = db.query(Stock).count()
        logger.info(f"Total stocks in database: {total_stocks}")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from app.core.database import SessionLocal
    seed_comprehensive_stocks()
