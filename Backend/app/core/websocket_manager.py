"""
WebSocket Manager for Real-time Updates
Handles WebSocket connections and broadcasts real-time data updates
"""

import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        # Store active connections by type
        self.leaderboard_connections: Set[WebSocket] = set()
        self.portfolio_connections: Dict[int, Set[WebSocket]] = {}  # user_id -> connections
        self.stock_connections: Dict[str, Set[WebSocket]] = {}     # symbol -> connections
        
    async def connect_leaderboard(self, websocket: WebSocket):
        """Connect to leaderboard updates"""
        await websocket.accept()
        self.leaderboard_connections.add(websocket)
        logger.info(f"Leaderboard connection added. Total: {len(self.leaderboard_connections)}")
        
    async def connect_portfolio(self, websocket: WebSocket, user_id: int):
        """Connect to portfolio updates for a specific user"""
        await websocket.accept()
        if user_id not in self.portfolio_connections:
            self.portfolio_connections[user_id] = set()
        self.portfolio_connections[user_id].add(websocket)
        logger.info(f"Portfolio connection added for user {user_id}")
        
    async def connect_stock(self, websocket: WebSocket, symbol: str):
        """Connect to stock price updates for a specific symbol"""
        await websocket.accept()
        if symbol not in self.stock_connections:
            self.stock_connections[symbol] = set()
        self.stock_connections[symbol].add(websocket)
        logger.info(f"Stock connection added for {symbol}")
        
    def disconnect_leaderboard(self, websocket: WebSocket):
        """Disconnect from leaderboard updates"""
        self.leaderboard_connections.discard(websocket)
        logger.info(f"Leaderboard connection removed. Total: {len(self.leaderboard_connections)}")
        
    def disconnect_portfolio(self, websocket: WebSocket, user_id: int):
        """Disconnect from portfolio updates"""
        if user_id in self.portfolio_connections:
            self.portfolio_connections[user_id].discard(websocket)
            if not self.portfolio_connections[user_id]:
                del self.portfolio_connections[user_id]
        logger.info(f"Portfolio connection removed for user {user_id}")
        
    def disconnect_stock(self, websocket: WebSocket, symbol: str):
        """Disconnect from stock updates"""
        if symbol in self.stock_connections:
            self.stock_connections[symbol].discard(websocket)
            if not self.stock_connections[symbol]:
                del self.stock_connections[symbol]
        logger.info(f"Stock connection removed for {symbol}")
        
    async def broadcast_leaderboard_update(self, leaderboard_data: dict):
        """Broadcast leaderboard updates to all connected clients"""
        if not self.leaderboard_connections:
            return
            
        message = {
            "type": "leaderboard_update",
            "data": leaderboard_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        disconnected = set()
        for connection in self.leaderboard_connections:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to leaderboard connection: {e}")
                disconnected.add(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.leaderboard_connections.discard(connection)
            
        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected leaderboard connections")
            
    async def broadcast_portfolio_update(self, user_id: int, portfolio_data: dict):
        """Broadcast portfolio updates to specific user's connections"""
        if user_id not in self.portfolio_connections:
            return
            
        message = {
            "type": "portfolio_update",
            "data": portfolio_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        disconnected = set()
        for connection in self.portfolio_connections[user_id]:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to portfolio connection: {e}")
                disconnected.add(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.portfolio_connections[user_id].discard(connection)
            
        if not self.portfolio_connections[user_id]:
            del self.portfolio_connections[user_id]
            
    async def broadcast_stock_update(self, symbol: str, stock_data: dict):
        """Broadcast stock price updates to specific stock's connections"""
        if symbol not in self.stock_connections:
            return
            
        message = {
            "type": "stock_update",
            "data": stock_data,
            "symbol": symbol,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        disconnected = set()
        for connection in self.stock_connections[symbol]:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to stock connection: {e}")
                disconnected.add(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.stock_connections[symbol].discard(connection)
            
        if not self.stock_connections[symbol]:
            del self.stock_connections[symbol]
            
    def get_connection_stats(self) -> dict:
        """Get statistics about active connections"""
        return {
            "leaderboard_connections": len(self.leaderboard_connections),
            "portfolio_connections": sum(len(conns) for conns in self.portfolio_connections.values()),
            "stock_connections": sum(len(conns) for conns in self.stock_connections.values()),
            "total_connections": (
                len(self.leaderboard_connections) + 
                sum(len(conns) for conns in self.portfolio_connections.values()) +
                sum(len(conns) for conns in self.stock_connections.values())
            )
        }


# Global connection manager instance
connection_manager = ConnectionManager()
