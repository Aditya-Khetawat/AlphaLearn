"use client";

import { useState, useEffect, useCallback } from "react";
import { stockService } from "@/services/api";
import { Stock } from "@/types";

export function useStocks(initialQuery = "") {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState(initialQuery);

  const fetchStocks = useCallback(
    async (searchQuery = query) => {
      try {
        setIsLoading(true);
        setError(null);

        // In a real app, this would call the API
        // For now, we'll simulate a delay and return mock data
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Mock stock data
        const mockStocks: Stock[] = [
          {
            id: 1,
            symbol: "AAPL",
            name: "Apple Inc.",
            currentPrice: 172.5,
            change: 0.75,
            changePercent: 0.43,
            previousClose: 171.75,
            open: 171.8,
            high: 173.2,
            low: 170.95,
            volume: 58234567,
          },
          {
            id: 2,
            symbol: "GOOGL",
            name: "Alphabet Inc.",
            currentPrice: 145.6,
            change: -0.4,
            changePercent: -0.27,
            previousClose: 146.0,
            open: 145.9,
            high: 146.5,
            low: 144.8,
            volume: 23456789,
          },
          // Add more mock stocks as needed
        ];

        // Filter stocks based on query if provided
        const filteredStocks = searchQuery
          ? mockStocks.filter(
              (stock) =>
                stock.symbol
                  .toLowerCase()
                  .includes(searchQuery.toLowerCase()) ||
                stock.name.toLowerCase().includes(searchQuery.toLowerCase())
            )
          : mockStocks;

        setStocks(filteredStocks);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch stocks");
        console.error("Error fetching stocks:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [query]
  );

  // Initial fetch
  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  // Search stocks with new query
  const searchStocks = useCallback(
    (newQuery: string) => {
      setQuery(newQuery);
      fetchStocks(newQuery);
    },
    [fetchStocks]
  );

  return { stocks, isLoading, error, searchStocks, refreshStocks: fetchStocks };
}

// For a specific stock with detailed information
export function useStockDetails(symbol: string) {
  const [stock, setStock] = useState<Stock | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStockDetails = useCallback(async () => {
    if (!symbol) return;

    try {
      setIsLoading(true);
      setError(null);

      // In a real app, this would call the API
      // For now, we'll simulate a delay and return mock data
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Mock detailed stock data
      const mockStock: Stock = {
        id:
          symbol === "AAPL"
            ? 1
            : symbol === "GOOGL"
            ? 2
            : symbol === "MSFT"
            ? 3
            : 99,
        symbol,
        name:
          symbol === "AAPL"
            ? "Apple Inc."
            : symbol === "GOOGL"
            ? "Alphabet Inc."
            : symbol === "MSFT"
            ? "Microsoft Corporation"
            : "Unknown Company",
        currentPrice:
          symbol === "AAPL"
            ? 172.5
            : symbol === "GOOGL"
            ? 145.6
            : symbol === "MSFT"
            ? 330.75
            : 100.0,
        change:
          symbol === "AAPL"
            ? 0.75
            : symbol === "GOOGL"
            ? -0.4
            : symbol === "MSFT"
            ? 1.25
            : 0.0,
        changePercent:
          symbol === "AAPL"
            ? 0.43
            : symbol === "GOOGL"
            ? -0.27
            : symbol === "MSFT"
            ? 0.38
            : 0.0,
        previousClose:
          symbol === "AAPL"
            ? 171.75
            : symbol === "GOOGL"
            ? 146.0
            : symbol === "MSFT"
            ? 329.5
            : 100.0,
        open:
          symbol === "AAPL"
            ? 171.8
            : symbol === "GOOGL"
            ? 145.9
            : symbol === "MSFT"
            ? 329.8
            : 100.0,
        high:
          symbol === "AAPL"
            ? 173.2
            : symbol === "GOOGL"
            ? 146.5
            : symbol === "MSFT"
            ? 331.5
            : 102.0,
        low:
          symbol === "AAPL"
            ? 170.95
            : symbol === "GOOGL"
            ? 144.8
            : symbol === "MSFT"
            ? 328.9
            : 98.0,
        volume:
          symbol === "AAPL"
            ? 58234567
            : symbol === "GOOGL"
            ? 23456789
            : symbol === "MSFT"
            ? 34567890
            : 1000000,
      };

      setStock(mockStock);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch stock details"
      );
      console.error(`Error fetching details for ${symbol}:`, err);
    } finally {
      setIsLoading(false);
    }
  }, [symbol]);

  // Fetch on symbol change
  useEffect(() => {
    fetchStockDetails();
  }, [fetchStockDetails]);

  return { stock, isLoading, error, refreshStock: fetchStockDetails };
}
