"""
Test script for comprehensive stock population

Run this to test the stock population system before integrating into FastAPI startup
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from app.services.stock_population import run_stock_population

if __name__ == "__main__":
    print("🚀 Testing comprehensive stock population system...")
    print("This will populate your database with 3000+ Indian stocks from NSE/BSE")
    print("Using yfinance for real-time price data with progress logging\n")
    
    try:
        run_stock_population()
        print("\n✅ Stock population test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Stock population test failed: {e}")
        raise
