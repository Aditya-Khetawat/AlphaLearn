import logging
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.crud import stock as stock_crud
from app.schemas.schemas import StockCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Indian stock symbols - NSE top companies
INDIAN_STOCKS = [
    # Major Indian indices
    {"symbol": "^NSEI", "name": "NIFTY 50", "sector": "Index"},
    {"symbol": "^BSESN", "name": "S&P BSE SENSEX", "sector": "Index"},
    
    # Top Indian stocks
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd", "sector": "Energy"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd", "sector": "Information Technology"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "sector": "Financial Services"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "sector": "Information Technology"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd", "sector": "Consumer Goods"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Ltd", "sector": "Financial Services"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Financial Services"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd", "sector": "Financial Services"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd", "sector": "Communication Services"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd", "sector": "Financial Services"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies Ltd", "sector": "Information Technology"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Ltd", "sector": "Industrials"},
    {"symbol": "WIPRO.NS", "name": "Wipro Ltd", "sector": "Information Technology"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Ltd", "sector": "Financial Services"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Ltd", "sector": "Consumer Goods"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Ltd", "sector": "Automobile"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Ltd", "sector": "Materials"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "sector": "Automobile"}
]


def fetch_stock_data(symbols):
    """
    Fetch current price data for a list of stock symbols using yfinance
    """
    logger.info(f"Fetching data for {len(symbols)} stocks")
    try:
        data = yf.download(symbols, period="2d")['Close']
        if len(symbols) == 1:
            # Handle single symbol case
            data = pd.DataFrame({symbols[0]: data})
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()


def populate_stocks(db: Session) -> None:
    """
    Add initial stock data to the database
    """
    # Extract symbols for fetching data
    symbols = [stock["symbol"] for stock in INDIAN_STOCKS]
    
    # Fetch stock prices
    price_data = fetch_stock_data(symbols)
    
    if price_data.empty:
        logger.error("Failed to fetch stock data")
        return
    
    # Get latest and previous closing prices
    if len(price_data) >= 2:
        latest_prices = price_data.iloc[-1]
        previous_prices = price_data.iloc[-2]
    else:
        latest_prices = price_data.iloc[-1]
        previous_prices = latest_prices
    
    # Create stocks in database
    for stock_info in INDIAN_STOCKS:
        symbol = stock_info["symbol"]
        try:
            # Clean up the symbol for database storage
            db_symbol = symbol.replace(".NS", "")
            
            # Get prices
            current_price = float(latest_prices.get(symbol, 0))
            previous_close = float(previous_prices.get(symbol, 0))
            
            # Skip if couldn't get price
            if current_price <= 0:
                logger.warning(f"Skipping {symbol} due to invalid price data")
                continue
            
            # Create stock entry
            stock_data = StockCreate(
                symbol=db_symbol,
                name=stock_info["name"],
                current_price=current_price,
                previous_close=previous_close,
                exchange="NSE",
                sector=stock_info.get("sector")
            )
            
            # Check if stock already exists
            existing_stock = stock_crud.get_by_symbol(db, symbol=db_symbol)
            if existing_stock:
                logger.info(f"Stock {db_symbol} already exists, updating price")
                stock_crud.update(db, db_obj=existing_stock, obj_in={
                    "current_price": current_price,
                    "previous_close": previous_close
                })
            else:
                logger.info(f"Adding stock {db_symbol} to database")
                stock_crud.create(db, obj_in=stock_data)
                
        except Exception as e:
            logger.error(f"Error adding stock {symbol}: {e}")
    
    logger.info("Finished populating stocks")


def init_db(db: Session) -> None:
    """
    Initialize database with necessary data
    """
    # Add initial stock data
    populate_stocks(db)
