#!/usr/bin/env python3
"""
WebSocket Test Script
Tests the AlphaLearn WebSocket endpoints for real-time functionality
"""
import asyncio
import websockets
import json
import time

async def test_leaderboard_websocket():
    """Test the leaderboard WebSocket endpoint"""
    uri = "ws://127.0.0.1:8000/api/v1/ws/leaderboard"
    
    try:
        print("🔗 Connecting to leaderboard WebSocket...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to leaderboard WebSocket!")
            
            # Wait for initial data
            print("📡 Waiting for leaderboard data...")
            
            # Listen for messages for 10 seconds
            timeout = 10
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    print("📊 Received leaderboard update:")
                    print(f"   Total users: {data.get('total_users', 'N/A')}")
                    print(f"   Leaderboard entries: {len(data.get('leaderboard', []))}")
                    
                    if data.get('leaderboard'):
                        top_trader = data['leaderboard'][0]
                        print(f"   Top trader: {top_trader.get('username', 'N/A')} (₹{top_trader.get('portfolio_value', 0):,.2f})")
                    
                    print("---")
                    break  # Exit after receiving first message
                    
                except asyncio.TimeoutError:
                    print("⏰ No message received (timeout)")
                    continue
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    continue
            
            print("✅ Test completed successfully!")
            
    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ Connection rejected: {e}")
        print("   Check if WebSocket endpoint is properly configured")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

async def main():
    """Run WebSocket tests"""
    print("🚀 AlphaLearn WebSocket Test Suite")
    print("=" * 50)
    
    await test_leaderboard_websocket()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
