"use client";

import { useState, useEffect, useCallback } from "react";
import { leaderboardService } from "@/services/api";
import { LeaderboardEntry } from "@/types";

export function useLeaderboard(timeframe = "all") {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = useCallback(
    async (tf = timeframe) => {
      try {
        setIsLoading(true);
        setError(null);

        // In a real app, this would call the API
        // For now, we'll simulate a delay and return mock data
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Mock leaderboard data
        const mockLeaderboard: LeaderboardEntry[] = [
          {
            userId: "user-2",
            userName: "Emma Johnson",
            userAvatar: "/placeholder-user.jpg",
            portfolioValue: 12500.75,
            totalReturn: 2500.75,
            totalReturnPercent: 25.01,
            rank: 1,
          },
          {
            userId: "user-1",
            userName: "John Doe",
            userAvatar: "/placeholder-user.jpg",
            portfolioValue: 10093.25,
            totalReturn: 93.25,
            totalReturnPercent: 0.93,
            rank: 2,
          },
          {
            userId: "user-3",
            userName: "Alex Smith",
            userAvatar: "/placeholder-user.jpg",
            portfolioValue: 9850.5,
            totalReturn: -149.5,
            totalReturnPercent: -1.49,
            rank: 3,
          },
          {
            userId: "user-4",
            userName: "Maria Garcia",
            userAvatar: "/placeholder-user.jpg",
            portfolioValue: 9750.25,
            totalReturn: 750.25,
            totalReturnPercent: 8.33,
            rank: 4,
          },
          {
            userId: "user-5",
            userName: "David Brown",
            userAvatar: "/placeholder-user.jpg",
            portfolioValue: 9500.0,
            totalReturn: 500.0,
            totalReturnPercent: 5.56,
            rank: 5,
          },
        ];

        setLeaderboard(mockLeaderboard);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch leaderboard"
        );
        console.error("Error fetching leaderboard:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [timeframe]
  );

  // Initial fetch
  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  // Change timeframe
  const changeTimeframe = useCallback(
    (newTimeframe: string) => {
      fetchLeaderboard(newTimeframe);
    },
    [fetchLeaderboard]
  );

  return {
    leaderboard,
    isLoading,
    error,
    refreshLeaderboard: fetchLeaderboard,
    changeTimeframe,
  };
}
