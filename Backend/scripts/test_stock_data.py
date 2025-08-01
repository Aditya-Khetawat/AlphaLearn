"""
Script to test the stock data service without starting the full API

Run with: python -m scripts.test_stock_data
"""

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to sys.path to allow imports from the app
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Now we can import from the app
from app.services.stock_data import StockDataService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stock_data():
    """Test fetching stock data from Yahoo Finance"""
    # List of some popular Indian stocks
    symbols = [
        "RELIANCE",
        "TCS",
        "HDFCBANK",
        "INFY",
        "SBIN",
        "BAJFINANCE",
        "WIPRO",
        "ICICIBANK"
    ]
    
    logger.info(f"Testing stock data service with symbols: {symbols}")
    
    # Fetch data for multiple stocks
    results = StockDataService.get_multiple_stocks(symbols)
    
    # Print results in a table format
    logger.info(f"\n{'Symbol':<10} {'Name':<30} {'Price':<10} {'Change':<10} {'Change %':<10}")
    logger.info("-" * 70)
    
    for stock in results:
        logger.info(
            f"{stock['symbol']:<10} "
            f"{stock['name'][:28]:<30} "
            f"{stock['current_price']:<10.2f} "
            f"{stock['change']:<10.2f} "
            f"{stock['change_percent']:<10.2f}%"
        )

if __name__ == "__main__":
    test_stock_data()
