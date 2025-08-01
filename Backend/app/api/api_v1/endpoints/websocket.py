"""
WebSocket endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import asyncio
import logging

from app.core.database import get_db
from app.core.websocket_manager import connection_manager
from app.api.api_v1.endpoints.leaderboard import get_leaderboard

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/leaderboard")
async def websocket_leaderboard(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time leaderboard updates
    """
    logger.info("🔗 WebSocket connection attempt for leaderboard")
    await connection_manager.connect_leaderboard(websocket)
    logger.info("✅ WebSocket connected to leaderboard")
    
    try:
        # Send initial leaderboard data
        initial_data = get_leaderboard(limit=50, db=db)
        await websocket.send_json(initial_data)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (like ping/pong)
                data = await websocket.receive_text()
                
                # Handle client messages
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "refresh":
                    # Send updated leaderboard data
                    updated_data = get_leaderboard(limit=50, db=db)
                    await websocket.send_json(updated_data)
                    
            except asyncio.TimeoutError:
                # Send periodic updates (every 30 seconds)
                updated_data = get_leaderboard(limit=50, db=db)
                await websocket.send_json({
                    "type": "leaderboard_update",
                    "data": updated_data
                })
                
    except WebSocketDisconnect:
        connection_manager.disconnect_leaderboard(websocket)
        logger.info("Leaderboard WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Error in leaderboard WebSocket: {e}")
        connection_manager.disconnect_leaderboard(websocket)


@router.websocket("/portfolio/{user_id}")
async def websocket_portfolio(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time portfolio updates for a specific user
    """
    await connection_manager.connect_portfolio(websocket, user_id)
    
    try:
        # Send initial portfolio data
        # TODO: Get initial portfolio data for the user
        await websocket.send_json({
            "type": "initial_portfolio",
            "data": {"message": f"Connected to portfolio updates for user {user_id}"}
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send periodic portfolio updates
                await websocket.send_json({
                    "type": "portfolio_heartbeat",
                    "data": {"user_id": user_id, "status": "connected"}
                })
                
    except WebSocketDisconnect:
        connection_manager.disconnect_portfolio(websocket, user_id)
        logger.info(f"Portfolio WebSocket client disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"Error in portfolio WebSocket for user {user_id}: {e}")
        connection_manager.disconnect_portfolio(websocket, user_id)


@router.websocket("/stock/{symbol}")
async def websocket_stock(websocket: WebSocket, symbol: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time stock price updates for a specific symbol
    """
    symbol = symbol.upper()
    await connection_manager.connect_stock(websocket, symbol)
    
    try:
        # Send initial stock data
        await websocket.send_json({
            "type": "initial_stock",
            "data": {"symbol": symbol, "message": f"Connected to price updates for {symbol}"}
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send periodic stock updates
                await websocket.send_json({
                    "type": "stock_heartbeat",
                    "data": {"symbol": symbol, "status": "connected"}
                })
                
    except WebSocketDisconnect:
        connection_manager.disconnect_stock(websocket, symbol)
        logger.info(f"Stock WebSocket client disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Error in stock WebSocket for {symbol}: {e}")
        connection_manager.disconnect_stock(websocket, symbol)


@router.get("/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics
    """
    return {
        "connections": connection_manager.get_connection_stats(),
        "message": "WebSocket connection statistics"
    }
