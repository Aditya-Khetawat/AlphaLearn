"use client";

import { useState, useEffect, useCallback } from "react";
import { portfolioService } from "@/services/api";
import { Portfolio, Position } from "@/types";

export function usePortfolio() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // In a real app, this would call the API
      // For now, we'll simulate a delay and return mock data
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Mock portfolio data
      const mockPortfolio: Portfolio = {
        positions: [
          {
            symbol: "AAPL",
            shares: 10,
            averageCost: 168.3,
            currentValue: 1725.0,
            totalReturn: 42.0,
            totalReturnPercent: 2.49,
          },
          {
            symbol: "MSFT",
            shares: 5,
            averageCost: 320.5,
            currentValue: 1653.75,
            totalReturn: 51.25,
            totalReturnPercent: 3.19,
          },
        ],
        totalValue: 3378.75,
        totalCost: 3285.5,
        totalReturn: 93.25,
        totalReturnPercent: 2.84,
        cash: 6714.5,
      };

      setPortfolio(mockPortfolio);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch portfolio"
      );
      console.error("Error fetching portfolio:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  // Buy stock functionality
  const buyStock = useCallback(
    async (symbol: string, shares: number, price: number) => {
      try {
        setIsLoading(true);
        setError(null);

        // In a real app, this would call the API
        // For now, we'll simulate a delay and update our local state
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Check if we have a portfolio loaded
        if (!portfolio) throw new Error("Portfolio not loaded");

        // Calculate cost
        const cost = shares * price;

        // Check if user has enough cash
        if (portfolio.cash < cost) {
          throw new Error("Insufficient funds");
        }

        // Find existing position if any
        const existingPosition = portfolio.positions.find(
          (p) => p.symbol === symbol
        );
        let updatedPositions = [...portfolio.positions];

        if (existingPosition) {
          // Update existing position
          const totalShares = existingPosition.shares + shares;
          const totalCost =
            existingPosition.shares * existingPosition.averageCost + cost;
          const newAverageCost = totalCost / totalShares;

          updatedPositions = updatedPositions.map((p) =>
            p.symbol === symbol
              ? {
                  ...p,
                  shares: totalShares,
                  averageCost: newAverageCost,
                  currentValue: totalShares * price,
                  totalReturn: (price - newAverageCost) * totalShares,
                  totalReturnPercent: (price / newAverageCost - 1) * 100,
                }
              : p
          );
        } else {
          // Add new position
          updatedPositions.push({
            symbol,
            shares,
            averageCost: price,
            currentValue: shares * price,
            totalReturn: 0,
            totalReturnPercent: 0,
          });
        }

        // Calculate new totals
        const newTotalCost = updatedPositions.reduce(
          (sum, p) => sum + p.shares * p.averageCost,
          0
        );
        const newTotalValue = updatedPositions.reduce(
          (sum, p) => sum + p.currentValue,
          0
        );
        const newTotalReturn = newTotalValue - newTotalCost;
        const newTotalReturnPercent = (newTotalReturn / newTotalCost) * 100;
        const newCash = portfolio.cash - cost;

        // Update state
        setPortfolio({
          positions: updatedPositions,
          totalValue: newTotalValue,
          totalCost: newTotalCost,
          totalReturn: newTotalReturn,
          totalReturnPercent: newTotalReturnPercent,
          cash: newCash,
        });

        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to buy stock");
        console.error("Error buying stock:", err);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [portfolio]
  );

  // Sell stock functionality
  const sellStock = useCallback(
    async (symbol: string, shares: number, price: number) => {
      try {
        setIsLoading(true);
        setError(null);

        // In a real app, this would call the API
        // For now, we'll simulate a delay and update our local state
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Check if we have a portfolio loaded
        if (!portfolio) throw new Error("Portfolio not loaded");

        // Find position
        const position = portfolio.positions.find((p) => p.symbol === symbol);

        if (!position) {
          throw new Error("Position not found");
        }

        if (position.shares < shares) {
          throw new Error("Not enough shares");
        }

        // Calculate sale value
        const saleValue = shares * price;

        // Update positions
        let updatedPositions = [...portfolio.positions];

        if (position.shares === shares) {
          // Remove position if selling all shares
          updatedPositions = updatedPositions.filter(
            (p) => p.symbol !== symbol
          );
        } else {
          // Update position if selling some shares
          updatedPositions = updatedPositions.map((p) =>
            p.symbol === symbol
              ? {
                  ...p,
                  shares: p.shares - shares,
                  currentValue: (p.shares - shares) * price,
                  totalReturn:
                    (p.shares - shares) * price -
                    (p.shares - shares) * p.averageCost,
                  totalReturnPercent: (price / p.averageCost - 1) * 100,
                }
              : p
          );
        }

        // Calculate new totals
        const newTotalCost = updatedPositions.reduce(
          (sum, p) => sum + p.shares * p.averageCost,
          0
        );
        const newTotalValue = updatedPositions.reduce(
          (sum, p) => sum + p.currentValue,
          0
        );
        const newTotalReturn = newTotalValue - newTotalCost;
        const newTotalReturnPercent =
          newTotalCost > 0 ? (newTotalReturn / newTotalCost) * 100 : 0;
        const newCash = portfolio.cash + saleValue;

        // Update state
        setPortfolio({
          positions: updatedPositions,
          totalValue: newTotalValue,
          totalCost: newTotalCost,
          totalReturn: newTotalReturn,
          totalReturnPercent: newTotalReturnPercent,
          cash: newCash,
        });

        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to sell stock");
        console.error("Error selling stock:", err);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [portfolio]
  );

  return {
    portfolio,
    isLoading,
    error,
    refreshPortfolio: fetchPortfolio,
    buyStock,
    sellStock,
  };
}
