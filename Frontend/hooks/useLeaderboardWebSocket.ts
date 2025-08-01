/**
 * WebSocket hook for real-time leaderboard updates
 */

import { useEffect, useRef, useState } from "react";
import { LeaderboardEntry } from "@/types";

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp?: number;
}

interface UseLeaderboardWebSocketReturn {
  leaderboard: LeaderboardEntry[];
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export function useLeaderboardWebSocket(): UseLeaderboardWebSocketReturn {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const mountedRef = useRef(true);
  const maxReconnectAttempts = 5;

  const transformLeaderboardData = (apiData: any[]): LeaderboardEntry[] => {
    return apiData.map((entry: any) => ({
      rank: entry.rank,
      userId: entry.user_id?.toString() || entry.userId,
      userName: entry.full_name || entry.username || entry.userName,
      userAvatar: "/placeholder-user.jpg",
      portfolioValue: entry.portfolio_value || entry.portfolioValue,
      totalReturn: entry.total_return || entry.totalReturn,
      totalReturnPercent:
        entry.total_return_percent || entry.totalReturnPercent,
      investedValue: entry.invested_value || entry.investedValue,
      positionsValue: entry.positions_value || entry.positionsValue,
      cashBalance: entry.cash_balance || entry.cashBalance,
      activePositions: entry.active_positions || entry.activePositions || 0,
    }));
  };

  const cleanup = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;

      if (
        wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING
      ) {
        wsRef.current.close(1000, "Component cleanup");
      }
      wsRef.current = null;
    }
  };

  const connect = () => {
    if (!mountedRef.current) return;

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    cleanup(); // Clean up any existing connection

    try {
      // Use ws:// for development, wss:// for production
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.hostname}:8000/api/v1/ws/leaderboard`;

      console.log(`Connecting to WebSocket: ${wsUrl}`);
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        if (!mountedRef.current) return;
        console.log("Leaderboard WebSocket connected");
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          // Handle ping/pong messages
          if (event.data === "pong") {
            console.log("Received pong from server");
            return;
          }

          const data = JSON.parse(event.data);
          console.log("Received WebSocket message:", data);

          // Handle direct leaderboard data format from backend
          if (data.leaderboard && Array.isArray(data.leaderboard)) {
            const transformedData = transformLeaderboardData(data.leaderboard);
            setLeaderboard(transformedData);
            console.log(
              `Updated leaderboard with ${transformedData.length} entries`
            );
          } else if (Array.isArray(data)) {
            // Handle array format directly
            const transformedData = transformLeaderboardData(data);
            setLeaderboard(transformedData);
            console.log(
              `Updated leaderboard with ${transformedData.length} entries`
            );
          } else {
            console.log(
              "Received data does not contain leaderboard array:",
              data
            );
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        if (!mountedRef.current) return;

        console.log(
          "Leaderboard WebSocket disconnected:",
          event.code,
          event.reason
        );
        setIsConnected(false);

        // Attempt to reconnect if not a manual close
        if (
          event.code !== 1000 &&
          reconnectAttempts.current < maxReconnectAttempts
        ) {
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttempts.current),
            30000
          );
          console.log(`Attempting to reconnect in ${delay}ms...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              reconnectAttempts.current++;
              connect();
            }
          }, delay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          setError(
            "Unable to establish WebSocket connection after multiple attempts"
          );
        }
      };

      wsRef.current.onerror = () => {
        if (!mountedRef.current) return;

        console.error("Leaderboard WebSocket error occurred");
        setError("WebSocket connection error");
        setIsConnected(false);
      };
    } catch (error) {
      if (!mountedRef.current) return;

      console.error("Error creating WebSocket:", error);
      setError("Failed to create WebSocket connection");
    }
  };

  const reconnect = () => {
    reconnectAttempts.current = 0;
    setError(null);
    connect();
  };

  // Setup and cleanup
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      cleanup();
    };
  }, []); // Empty dependency array

  return {
    leaderboard,
    isConnected,
    error,
    reconnect,
  };
}
