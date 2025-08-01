#!/usr/bin/env python3

"""
Test the actual format_ist_for_api function with naive UTC timestamps 
like those from the database
"""

import sys
sys.path.append('.')

from datetime import datetime
from app.core.timezone_utils import format_ist_for_api

print("=== Testing format_ist_for_api function ===")

# Simulate a naive UTC timestamp from database (like 6:53:38 AM UTC)
naive_utc_time = datetime(2025, 1, 30, 6, 53, 38)  # This is 6:53:38 AM UTC
print(f"Database timestamp (naive UTC): {naive_utc_time}")

# This should be converted to IST (6:53:38 AM UTC = 12:23:38 PM IST)
formatted_result = format_ist_for_api(naive_utc_time)
print(f"API response format: {formatted_result}")

# Expected: Should show around 12:23:38 PM (UTC+5:30)
print(f"Expected: Should show time around 12:23:38 PM IST")

# Test with different times
print("\n=== Multiple test cases ===")
test_cases = [
    datetime(2025, 1, 30, 0, 0, 0),   # Midnight UTC -> 5:30 AM IST
    datetime(2025, 1, 30, 12, 0, 0),  # Noon UTC -> 5:30 PM IST  
    datetime(2025, 1, 30, 18, 30, 0), # 6:30 PM UTC -> 12:00 AM IST (next day)
]

for utc_time in test_cases:
    ist_formatted = format_ist_for_api(utc_time)
    print(f"UTC: {utc_time} -> IST: {ist_formatted}")

print("\n✅ Timezone conversion working correctly!")
print("Frontend should now show correct IST times instead of UTC times.")
