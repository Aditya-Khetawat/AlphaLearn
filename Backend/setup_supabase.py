"""
Setup script for initializing Supabase database with the required tables.

This script uses the Supabase Python client to execute SQL queries to create the necessary
tables for the AlphaLearn application.
"""

import logging
import os
from app.core.supabase_client import get_supabase_client
from app.core.config import settings
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_supabase():
    """Create tables in Supabase"""
    logger.info("Setting up Supabase database tables")
    
    supabase = get_supabase_client()
    
    try:
        # Test the connection
        response = supabase.table('_test_connection_').select('*', count='exact').limit(1).execute()
        logger.info("Successfully connected to Supabase!")
        
        # In a real implementation, you would use Supabase migrations
        # or create all your tables here with proper SQL commands
        # SQL statements for creating tables
        SQL_STATEMENTS = [
            """
            -- Users table (extends Supabase auth.users)
            CREATE TABLE IF NOT EXISTS public.users (
                id UUID REFERENCES auth.users(id) PRIMARY KEY,
                full_name TEXT,
                balance NUMERIC NOT NULL DEFAULT 100000,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
            );
            """,
            """
            -- Enable RLS on users table
            ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
            """,
            """
            -- Create policy for users to access only their own data
            DROP POLICY IF EXISTS "Users can view and update their own data" ON public.users;
            CREATE POLICY "Users can view and update their own data" ON public.users
                FOR ALL USING (auth.uid() = id);
            """,
            """
            -- Stocks table
            CREATE TABLE IF NOT EXISTS public.stocks (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                current_price NUMERIC NOT NULL,
                previous_close NUMERIC,
                change NUMERIC,
                change_percent NUMERIC,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
            );
            """,
            """
            -- Portfolio positions table
            CREATE TABLE IF NOT EXISTS public.positions (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES public.users(id) NOT NULL,
                stock_id INTEGER REFERENCES public.stocks(id) NOT NULL,
                shares NUMERIC NOT NULL,
                average_cost NUMERIC NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
                UNIQUE(user_id, stock_id)
            );
            """,
            """
            -- Enable RLS on positions table
            ALTER TABLE public.positions ENABLE ROW LEVEL SECURITY;
            """,
            """
            -- Create policy for users to access only their own positions
            DROP POLICY IF EXISTS "Users can view and update their own positions" ON public.positions;
            CREATE POLICY "Users can view and update their own positions" ON public.positions
                FOR ALL USING (auth.uid() = user_id);
            """,
            """
            -- Transactions table
            CREATE TABLE IF NOT EXISTS public.transactions (
                id SERIAL PRIMARY KEY,
                user_id UUID REFERENCES public.users(id) NOT NULL,
                stock_id INTEGER REFERENCES public.stocks(id) NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('BUY', 'SELL')),
                shares NUMERIC NOT NULL,
                price NUMERIC NOT NULL,
                total NUMERIC NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
            );
            """,
            """
            -- Enable RLS on transactions table
            ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
            """,
            """
            -- Create policy for users to access only their own transactions
            DROP POLICY IF EXISTS "Users can view their own transactions" ON public.transactions;
            CREATE POLICY "Users can view their own transactions" ON public.transactions
                FOR ALL USING (auth.uid() = user_id);
            """,
            """
            -- Add trigger for updating user balance after inserting transactions
            CREATE OR REPLACE FUNCTION update_user_balance_after_transaction()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.type = 'BUY' THEN
                    UPDATE public.users
                    SET balance = balance - NEW.total
                    WHERE id = NEW.user_id;
                ELSIF NEW.type = 'SELL' THEN
                    UPDATE public.users
                    SET balance = balance + NEW.total
                    WHERE id = NEW.user_id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            """
            DROP TRIGGER IF EXISTS trigger_update_balance ON public.transactions;
            CREATE TRIGGER trigger_update_balance
            AFTER INSERT ON public.transactions
            FOR EACH ROW
            EXECUTE FUNCTION update_user_balance_after_transaction();
            """
        ]

        # Insert sample Indian stocks
        SAMPLE_STOCKS = [
            """
            INSERT INTO public.stocks (symbol, name, current_price, previous_close, change, change_percent)
            VALUES 
                ('RELIANCE', 'Reliance Industries Ltd', 2875.30, 2842.55, 32.75, 1.15),
                ('TCS', 'Tata Consultancy Services Ltd', 3642.15, 3670.65, -28.50, -0.78),
                ('HDFCBANK', 'HDFC Bank Ltd', 1578.25, 1559.80, 18.45, 1.18),
                ('INFY', 'Infosys Ltd', 1425.80, 1438.15, -12.35, -0.86),
                ('SBIN', 'State Bank of India', 687.50, 682.25, 5.25, 0.77),
                ('HDFC', 'Housing Development Finance Corporation Ltd', 2740.40, 2735.65, 4.75, 0.17),
                ('ICICIBANK', 'ICICI Bank Ltd', 956.75, 948.30, 8.45, 0.89),
                ('BAJFINANCE', 'Bajaj Finance Ltd', 6758.50, 6795.20, -36.70, -0.54),
                ('BHARTIARTL', 'Bharti Airtel Ltd', 842.60, 835.90, 6.70, 0.80),
                ('LT', 'Larsen & Toubro Ltd', 2450.35, 2432.65, 17.70, 0.73)
            ON CONFLICT (symbol) DO UPDATE SET 
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                previous_close = EXCLUDED.previous_close,
                change = EXCLUDED.change,
                change_percent = EXCLUDED.change_percent,
                updated_at = NOW();
            """
        ]

        # Execute SQL statements
        logger.info("Creating database tables...")
        for sql in SQL_STATEMENTS:
            try:
                # We use RPC for admin-level SQL execution
                data = supabase.rpc('supabase_admin_query', {'query_text': sql}).execute()
                logger.info(f"SQL executed successfully.")
            except Exception as e:
                logger.error(f"Error executing SQL: {e}")
                
        # Insert sample stocks
        logger.info("\nInserting sample stock data...")
        for sql in SAMPLE_STOCKS:
            try:
                data = supabase.rpc('supabase_admin_query', {'query_text': sql}).execute()
                logger.info(f"Sample stocks inserted successfully.")
            except Exception as e:
                logger.error(f"Error inserting sample stocks: {e}")
        
        logger.info("\nDatabase setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Supabase: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("Setting up Supabase for AlphaLearn")
    setup_supabase()
    logger.info("Supabase setup complete")
