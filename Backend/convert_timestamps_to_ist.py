#!/usr/bin/env python3

"""
Script to convert existing UTC timestamps in database to IST
This fixes the issue where old transactions show wrong times
"""

import sys
import os
from datetime import datetime
import pytz

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.models import Transaction, User, Portfolio, Stock, Position
from app.core.database import SessionLocal
from app.core.timezone_utils import get_ist_now, utc_to_ist

def convert_utc_to_ist_in_database():
    """
    Convert all UTC timestamps in database tables to IST
    """
    print("🔄 Starting UTC to IST timestamp conversion...")
    
    db = SessionLocal()
    
    try:
        # Convert Transaction timestamps
        print("\n📊 Converting Transaction timestamps...")
        transactions = db.query(Transaction).all()
        transaction_count = 0
        
        for transaction in transactions:
            if transaction.timestamp:
                # Check if the timestamp is naive (no timezone info)
                if transaction.timestamp.tzinfo is None:
                    # Assume it's UTC and convert to IST
                    utc_time = pytz.utc.localize(transaction.timestamp)
                    ist_time = utc_to_ist(utc_time)
                    transaction.timestamp = ist_time
                    transaction_count += 1
                    print(f"  ✅ Transaction {transaction.id}: {utc_time} → {ist_time}")
        
        # Convert User timestamps
        print(f"\n👥 Converting User timestamps...")
        users = db.query(User).all()
        user_count = 0
        
        for user in users:
            updated = False
            if user.created_at and user.created_at.tzinfo is None:
                utc_time = pytz.utc.localize(user.created_at)
                user.created_at = utc_to_ist(utc_time)
                updated = True
            
            if user.updated_at and user.updated_at.tzinfo is None:
                utc_time = pytz.utc.localize(user.updated_at)
                user.updated_at = utc_to_ist(utc_time)
                updated = True
            
            if updated:
                user_count += 1
                print(f"  ✅ User {user.id}: timestamps converted to IST")
        
        # Convert Portfolio timestamps
        print(f"\n💼 Converting Portfolio timestamps...")
        portfolios = db.query(Portfolio).all()
        portfolio_count = 0
        
        for portfolio in portfolios:
            updated = False
            if portfolio.created_at and portfolio.created_at.tzinfo is None:
                utc_time = pytz.utc.localize(portfolio.created_at)
                portfolio.created_at = utc_to_ist(utc_time)
                updated = True
            
            if portfolio.updated_at and portfolio.updated_at.tzinfo is None:
                utc_time = pytz.utc.localize(portfolio.updated_at)
                portfolio.updated_at = utc_to_ist(utc_time)
                updated = True
            
            if updated:
                portfolio_count += 1
                print(f"  ✅ Portfolio {portfolio.id}: timestamps converted to IST")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Conversion completed successfully!")
        print(f"  📊 Transactions converted: {transaction_count}")
        print(f"  👥 Users converted: {user_count}")
        print(f"  💼 Portfolios converted: {portfolio_count}")
        print(f"\n✅ All timestamps are now in Indian Standard Time (IST)")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=== UTC to IST Database Timestamp Conversion ===")
    
    # Ask for confirmation
    response = input("\n⚠️  This will modify timestamp data in your database. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Conversion cancelled.")
        sys.exit(0)
    
    convert_utc_to_ist_in_database()
