import logging
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StockMarketService:
    """Service to handle stock market data operations"""
    
    @staticmethod
    def fetch_current_prices(symbols: List[str]) -> Dict[str, float]:
        """
        Fetch latest prices for a list of stock symbols
        
        Args:
            symbols: List of stock symbols (NSE format with .NS suffix)
            
        Returns:
            Dict mapping symbols to current prices
        """
        try:
            # Make sure symbols are in correct format for yfinance
            formatted_symbols = [
                f"{s}.NS" if not s.endswith(".NS") and not s.startswith("^") else s 
                for s in symbols
            ]
            
            # Fetch data
            data = yf.download(formatted_symbols, period="1d")
            
            # Extract closing prices
            if 'Close' in data:
                prices = data['Close'].iloc[-1].to_dict()
                
                # Clean up the keys to match our database symbols (without .NS)
                result = {}
                for symbol, price in prices.items():
                    clean_symbol = symbol.replace(".NS", "")
                    result[clean_symbol] = price
                
                return result
            else:
                logger.error("No Close data returned from yfinance")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching stock prices: {e}")
            return {}
    
    @staticmethod
    def fetch_stock_history(symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a stock
        
        Args:
            symbol: Stock symbol (without .NS suffix)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Format symbol for yfinance
            formatted_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") and not symbol.startswith("^") else symbol
            
            # Fetch data
            stock = yf.Ticker(formatted_symbol)
            hist = stock.history(period=period, interval=interval)
            
            if not hist.empty:
                return hist
            else:
                logger.warning(f"No historical data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return None
    
    @staticmethod
    def calculate_returns(prices: pd.Series, initial_investment: float) -> Dict[str, Any]:
        """
        Calculate investment returns
        
        Args:
            prices: Series of prices
            initial_investment: Initial investment amount
            
        Returns:
            Dict with return metrics
        """
        try:
            if prices is None or len(prices) < 2:
                return {
                    "absolute_return": 0,
                    "percent_return": 0,
                    "annualized_return": 0
                }
            
            # Calculate returns
            first_price = prices.iloc[0]
            last_price = prices.iloc[-1]
            
            if first_price <= 0:
                return {
                    "absolute_return": 0,
                    "percent_return": 0,
                    "annualized_return": 0
                }
            
            # Calculate metrics
            absolute_return = (last_price - first_price) * initial_investment / first_price
            percent_return = (last_price - first_price) / first_price * 100
            
            # Annualized return calculation
            days = (prices.index[-1] - prices.index[0]).days
            if days > 0:
                years = days / 365
                annualized_return = ((last_price / first_price) ** (1/years) - 1) * 100
            else:
                annualized_return = 0
            
            return {
                "absolute_return": absolute_return,
                "percent_return": percent_return,
                "annualized_return": annualized_return
            }
            
        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return {
                "absolute_return": 0,
                "percent_return": 0,
                "annualized_return": 0
            }
