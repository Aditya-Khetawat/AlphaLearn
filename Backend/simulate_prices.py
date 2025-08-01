"""
Script to simulate realistic price changes for demonstration
This will create varied price movements to show the system working
"""

import random
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import Stock

def simulate_price_changes():
    """Simulate realistic price changes for popular stocks"""
    
    print("🎯 Simulating realistic price changes for demonstration...")
    
    db = SessionLocal()
    
    try:
        # Get some popular stocks to simulate
        popular_symbols = ["TCS", "HDFCBANK", "ICICIBANK", "INFY", "RELIANCE"]
        
        for symbol in popular_symbols:
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            
            if stock:
                # Store current price as previous close
                stock.previous_close = stock.current_price
                
                # Generate a realistic price change (-5% to +5%)
                change_percent = random.uniform(-5.0, 5.0)
                new_price = stock.current_price * (1 + change_percent / 100)
                
                stock.current_price = new_price
                stock.last_updated = datetime.utcnow()
                
                print(f"📈 {symbol}: ₹{stock.previous_close:.2f} → ₹{new_price:.2f} ({change_percent:+.2f}%)")
        
        db.commit()
        print("✅ Price simulation completed!")
        
    except Exception as e:
        print(f"❌ Error simulating prices: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_price_changes()
