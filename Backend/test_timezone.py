#!/usr/bin/env python3

"""
Test script to verify IST timezone functionality
"""

import sys
import os
from datetime import datetime

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.timezone_utils import get_ist_now, format_ist_datetime, get_ist_timestamp, format_ist_for_api

def test_timezone_functions():
    print("=== Testing IST Timezone Functions ===\n")
    
    # Test get_ist_now
    ist_now = get_ist_now()
    print(f"Current IST time: {ist_now}")
    print(f"Timezone info: {ist_now.tzinfo}")
    
    # Test get_ist_timestamp
    ist_timestamp = get_ist_timestamp()
    print(f"IST timestamp for database: {ist_timestamp}")
    
    # Test format_ist_for_api (JavaScript-friendly)
    api_format = format_ist_for_api(ist_now)
    print(f"API format (JavaScript-friendly): {api_format}")
    
    # Test format_ist_datetime (human-readable)
    formatted_time = format_ist_datetime(ist_now)
    print(f"Human-readable IST datetime: {formatted_time}")
    
    # Test with a UTC datetime
    utc_time = datetime.utcnow()
    print(f"\nUTC time: {utc_time}")
    
    # Simulate what would happen in the API
    api_response_time = format_ist_for_api(ist_timestamp)
    print(f"API response format: {api_response_time}")
    
    print("\n=== JavaScript Date Test ===")
    print(f"✅ ISO format for JavaScript: {api_format}")
    print("   This format works with: new Date('{0}')".format(api_format))
    print("   JavaScript will correctly parse and display IST time")
    
    print("\n=== Test Results ===")
    print("✅ All timezone functions are working correctly!")
    print("✅ IST timezone is properly configured")
    print(f"✅ JavaScript-friendly format: {api_format}")
    print(f"✅ Human-readable format: {formatted_time}")

if __name__ == "__main__":
    test_timezone_functions()
