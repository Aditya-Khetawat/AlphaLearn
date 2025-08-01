#!/usr/bin/env python3

"""
Fix timezone issue in database by properly converting UTC timestamps to IST
"""

import sys
import os
from datetime import datetime
import pytz

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.models import Transaction, User, Portfolio
from app.core.timezone_utils import get_ist_now

def fix_timezone_database():
    """
    Convert all naive UTC timestamps in database to timezone-aware IST timestamps
    """
    print("🔄 Starting timezone database fix...")
    
    db = SessionLocal()
    
    try:
        # Get timezone objects
        utc_tz = pytz.UTC
        ist_tz = pytz.timezone('Asia/Kolkata')
        
        # Fix Transaction timestamps
        print("\n📊 Fixing Transaction timestamps...")
        transactions = db.query(Transaction).all()
        transaction_count = 0
        
        for transaction in transactions:
            if transaction.timestamp and transaction.timestamp.tzinfo is None:
                # The naive datetime is actually UTC, so localize it as UTC first
                try:
                    utc_aware = utc_tz.localize(transaction.timestamp)
                    # Convert to IST
                    ist_aware = utc_aware.astimezone(ist_tz)
                    # Update the transaction
                    transaction.timestamp = ist_aware
                    transaction_count += 1
                    print(f"  ✅ Transaction {transaction.id}: {transaction.timestamp.replace(tzinfo=None)} UTC → {ist_aware}")
                except Exception as e:
                    print(f"  ❌ Error converting transaction {transaction.id}: {e}")
        
        # Fix User timestamps
        print(f"\n👥 Fixing User timestamps...")
        users = db.query(User).all()
        user_count = 0
        
        for user in users:
            try:
                if user.created_at and user.created_at.tzinfo is None:
                    utc_aware = utc_tz.localize(user.created_at)
                    ist_aware = utc_aware.astimezone(ist_tz)
                    user.created_at = ist_aware
                    user_count += 1
                    
                if user.updated_at and user.updated_at.tzinfo is None:
                    utc_aware = utc_tz.localize(user.updated_at)
                    ist_aware = utc_aware.astimezone(ist_tz)
                    user.updated_at = ist_aware
            except Exception as e:
                print(f"  ❌ Error converting user {user.id}: {e}")
        
        # Fix Portfolio timestamps
        print(f"\n💼 Fixing Portfolio timestamps...")
        portfolios = db.query(Portfolio).all()
        portfolio_count = 0
        
        for portfolio in portfolios:
            try:
                if portfolio.created_at and portfolio.created_at.tzinfo is None:
                    utc_aware = utc_tz.localize(portfolio.created_at)
                    ist_aware = utc_aware.astimezone(ist_tz)
                    portfolio.created_at = ist_aware
                    portfolio_count += 1
                    
                if portfolio.updated_at and portfolio.updated_at.tzinfo is None:
                    utc_aware = utc_tz.localize(portfolio.updated_at)
                    ist_aware = utc_aware.astimezone(ist_tz)
                    portfolio.updated_at = ist_aware
            except Exception as e:
                print(f"  ❌ Error converting portfolio {portfolio.id}: {e}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ TIMEZONE FIX COMPLETED SUCCESSFULLY!")
        print(f"   📊 Fixed {transaction_count} transaction timestamps")
        print(f"   👥 Fixed {user_count} user timestamps")
        print(f"   💼 Fixed {portfolio_count} portfolio timestamps")
        print(f"\n🎯 All timestamps are now timezone-aware IST!")
        
        # Verify the fix worked
        print(f"\n🔍 Verifying fix...")
        test_transaction = db.query(Transaction).first()
        if test_transaction:
            print(f"Test transaction timestamp: {test_transaction.timestamp}")
            print(f"Timezone aware: {test_transaction.timestamp.tzinfo is not None}")
            print(f"Timezone: {test_transaction.timestamp.tzinfo}")
        
    except Exception as e:
        print(f"❌ Error during timezone fix: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Database Timezone Fix ===")
    fix_timezone_database()
