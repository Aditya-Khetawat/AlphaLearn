"""
Stock market data service for fetching real-time stock prices.
This example uses yfinance to get Indian stock data.

Install with: pip install yfinance
"""

import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.models.models import Stock
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# NSE stock symbols need to be suffixed with .NS for Yahoo Finance
NSE_SUFFIX = ".NS" if settings.DEFAULT_EXCHANGE == "NSE" else ".BO"  # .BO for BSE

class StockDataService:
    """Service for fetching stock data from Yahoo Finance"""
    
    @staticmethod
    def get_stock_data(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current stock data for a single stock
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE" for Reliance Industries)
            
        Returns:
            Dictionary with stock data or None if failed
        """
        try:
            # Add .NS suffix for NSE stocks if not already present
            if not symbol.endswith(NSE_SUFFIX):
                yahoo_symbol = f"{symbol}{NSE_SUFFIX}"
            else:
                yahoo_symbol = symbol
                
            # Fetch the data
            stock = yf.Ticker(yahoo_symbol)
            
            # Get latest info
            info = stock.info
            
            # Get latest price data - we need this to get today's change
            hist = stock.history(period="2d")
            
            if hist.empty:
                logger.warning(f"No historical data found for {symbol}")
                return None
                
            # Calculate price change and change percentage
            current_price = info.get('regularMarketPrice', hist['Close'].iloc[-1])
            
            if len(hist) >= 2:
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                # If we only have today's data
                previous_close = info.get('regularMarketPreviousClose', current_price)
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                "symbol": symbol,
                "name": info.get('longName', symbol),
                "current_price": current_price,
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent,
                "high": info.get('dayHigh', current_price),
                "low": info.get('dayLow', current_price),
                "volume": info.get('volume', 0),
                "updated_at": datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_multiple_stocks(symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get data for multiple stocks
        
        Args:
            symbols: List of stock symbols (e.g., ["RELIANCE", "TCS"])
            
        Returns:
            List of dictionaries with stock data
        """
        results = []
        for symbol in symbols:
            stock_data = StockDataService.get_stock_data(symbol)
            if stock_data:
                results.append(stock_data)
        return results
    
    @staticmethod
    def update_stock_database(db_session, symbols: List[str]) -> None:
        """
        Update stock database with latest prices
        
        Args:
            db_session: SQLAlchemy database session
            symbols: List of stock symbols to update
        """
        stock_data_list = StockDataService.get_multiple_stocks(symbols)
        
        for stock_data in stock_data_list:
            # Check if stock exists in database
            db_stock = db_session.query(Stock).filter(Stock.symbol == stock_data["symbol"]).first()
            
            if db_stock:
                # Update existing stock
                for key, value in stock_data.items():
                    if hasattr(db_stock, key):
                        setattr(db_stock, key, value)
            else:
                # Create new stock
                new_stock = Stock(**stock_data)
                db_session.add(new_stock)
        
        db_session.commit()


# Example usage:
# from app.db.session import get_db
# symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY"]
# db = next(get_db())
# StockDataService.update_stock_database(db, symbols)
