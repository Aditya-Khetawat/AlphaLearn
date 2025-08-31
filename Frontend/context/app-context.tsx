"use client";

import {
  createContext,
  useContext,
  ReactNode,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import {
  User,
  Stock,
  Portfolio,
  Transaction,
  TransactionType,
  LeaderboardEntry,
  Position,
} from "@/types";

import {
  authAPI,
  userAPI,
  stockAPI,
  portfolioAPI,
  transactionAPI,
} from "@/lib/api";

import { leaderboardService } from "@/services/api";

import {
  apiUserToUser,
  apiPositionToStockPosition,
  apiStockToStock,
  apiTransactionToTransaction,
  apiPortfolioToPortfolio,
  ApiPortfolio,
  ApiStock,
  ApiTransaction,
} from "@/lib/api/mappers";

// Leaderboard will be populated from real user data when backend API is ready
// For now, keeping it empty to avoid showing fake users

// Sample stock data until API is connected
const mockStocks: Stock[] = [
  {
    id: 1,
    symbol: "RELIANCE",
    name: "Reliance Industries Ltd",
    currentPrice: 2875.3,
    change: 32.75,
    changePercent: 1.15,
  },
  {
    id: 2,
    symbol: "TCS",
    name: "Tata Consultancy Services Ltd",
    currentPrice: 3642.15,
    change: -28.5,
    changePercent: -0.78,
  },
  {
    id: 3,
    symbol: "HDFCBANK",
    name: "HDFC Bank Ltd",
    currentPrice: 1578.25,
    change: 18.45,
    changePercent: 1.18,
  },
  {
    id: 4,
    symbol: "INFY",
    name: "Infosys Ltd",
    currentPrice: 1442.6,
    change: 5.2,
    changePercent: 0.36,
  },
  {
    id: 5,
    symbol: "TATAMOTORS",
    name: "Tata Motors Ltd",
    currentPrice: 798.45,
    change: 12.35,
    changePercent: 1.57,
  },
];

interface AppState {
  user: User | null;
  stocks: Stock[];
  portfolio: Portfolio | null;
  transactions: Transaction[];
  leaderboard: LeaderboardEntry[];
  isLoading: {
    stocks: boolean;
    portfolio: boolean;
    transactions: boolean;
    leaderboard: boolean;
  };
  error: {
    stocks: string | null;
    portfolio: string | null;
    transactions: string | null;
    leaderboard: string | null;
  };
}

interface AppContextType extends AppState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  buyStock: (stockId: number, shares: number) => Promise<void>;
  sellStock: (stockId: number, shares: number) => Promise<void>;
  refreshStocks: () => Promise<void>;
  refreshPortfolio: () => Promise<void>;
  refreshTransactions: () => Promise<void>;
  refreshLeaderboard: () => Promise<void>;
  searchStocks: (query: string) => Promise<Stock[]>;
}

const initialState: AppState = {
  user: null,
  stocks: [],
  portfolio: null,
  transactions: [],
  leaderboard: [],
  isLoading: {
    stocks: false,
    portfolio: false,
    transactions: false,
    leaderboard: false,
  },
  error: {
    stocks: null,
    portfolio: null,
    transactions: null,
    leaderboard: null,
  },
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>(initialState);

  // Use refs to prevent useEffect dependency issues
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const lastRefreshTime = useRef<Record<string, number>>({});

  // Rate limiting helper
  const canRefresh = (key: string, minInterval: number = 30000): boolean => {
    const now = Date.now();
    const lastTime = lastRefreshTime.current[key] || 0;
    const canRefreshNow = now - lastTime >= minInterval;
    if (canRefreshNow) {
      lastRefreshTime.current[key] = now;
    }
    return canRefreshNow;
  };

  // Cleanup function
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, []);

  // Forward declarations for functions that reference each other
  const refreshStocks = useCallback(async () => {
    if (!mountedRef.current) return;

    // Rate limit: Only allow refresh every 30 seconds
    if (!canRefresh("stocks", 30000)) {
      console.log("Rate limited: Skipping stocks refresh");
      return;
    }

    try {
      console.log("Refreshing stocks data...");
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, stocks: true },
        error: { ...prevState.error, stocks: null },
      }));

      // First trigger a price update in the background
      try {
        console.log("Triggering backend price update...");
        await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
          }/stocks/update-prices?quick=true`,
          {
            method: "POST",
          }
        );
        console.log("Price update triggered successfully");

        // Wait a moment for the update to process
        await new Promise((resolve) => setTimeout(resolve, 2000));
      } catch (updateError) {
        console.warn("Could not trigger price update:", updateError);
        // Continue with stock fetch even if price update fails
      }

      // Load popular stocks initially for the main page and better search fallback
      // Full market access is available through search functionality
      const apiStocks: ApiStock[] = await stockAPI.getStocks({ limit: 200 }); // Load top 200 popular stocks

      if (!mountedRef.current) return; // Check again after async call

      const stocks = apiStocks.map(apiStockToStock);

      setState((prevState) => ({
        ...prevState,
        stocks,
        isLoading: { ...prevState.isLoading, stocks: false },
      }));
    } catch (error: any) {
      if (!mountedRef.current) return;
      console.error("Error loading stocks:", error);

      // Only fall back to mock data if API fails
      console.warn("Falling back to mock stock data due to API error");
      setState((prevState) => ({
        ...prevState,
        stocks: mockStocks,
        isLoading: { ...prevState.isLoading, stocks: false },
        error: {
          ...prevState.error,
          stocks: `API Error: ${
            error.message || "Failed to load stocks"
          }. Using mock data.`,
        },
      }));
    }
  }, []);

  const searchStocks = useCallback(
    async (query: string): Promise<Stock[]> => {
      try {
        if (!query.trim()) {
          return state.stocks; // Return popular stocks if no query
        }

        // Search with very high limit to access the entire market
        const apiStocks: ApiStock[] = await stockAPI.searchStocks(query, 1000);
        return apiStocks.map(apiStockToStock);
      } catch (error: any) {
        console.error("Error searching stocks:", error);

        // Fallback to local filtering if API search fails
        const filteredStocks = state.stocks.filter(
          (stock) =>
            stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        );
        return filteredStocks;
      }
    },
    [state.stocks]
  );

  const refreshPortfolio = useCallback(async () => {
    // Only try to load portfolio if user is logged in
    if (!state.user || !mountedRef.current) {
      return;
    }

    // Rate limit: Only allow refresh every 15 seconds
    if (!canRefresh("portfolio", 15000)) {
      console.log("Rate limited: Skipping portfolio refresh");
      return;
    }

    try {
      console.log("Refreshing portfolio data...");
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, portfolio: true },
        error: { ...prevState.error, portfolio: null },
      }));

      // Call portfolio API
      const apiPortfolio: ApiPortfolio = await portfolioAPI.getPortfolio();

      if (!mountedRef.current) return;

      // Convert API portfolio to our frontend portfolio using the mapper
      const portfolio = apiPortfolioToPortfolio(apiPortfolio);

      setState((prevState) => ({
        ...prevState,
        portfolio,
        isLoading: { ...prevState.isLoading, portfolio: false },
      }));

      // Update user balance
      if (state.user) {
        const updatedUser = {
          ...state.user,
          balance: apiPortfolio.cash_balance,
        };

        setState((prevState) => ({
          ...prevState,
          user: updatedUser,
        }));
      }
    } catch (error: any) {
      console.error("Error loading portfolio:", error);
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, portfolio: false },
        error: {
          ...prevState.error,
          portfolio: error.message || "Failed to load portfolio",
        },
      }));
    }
  }, [state.user]);

  const refreshTransactions = useCallback(async () => {
    // Only try to load transactions if user is logged in
    if (!state.user || !mountedRef.current) {
      return;
    }

    // Rate limit: Only allow refresh every 20 seconds
    if (!canRefresh("transactions", 20000)) {
      console.log("Rate limited: Skipping transactions refresh");
      return;
    }

    try {
      console.log("Refreshing transactions data...");
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, transactions: true },
        error: { ...prevState.error, transactions: null },
      }));

      // Call transactions history API
      const apiTransactions: ApiTransaction[] =
        await transactionAPI.getTransactionHistory();

      if (!mountedRef.current) return;

      const transactions = apiTransactions.map(apiTransactionToTransaction);

      setState((prevState) => ({
        ...prevState,
        transactions,
        isLoading: { ...prevState.isLoading, transactions: false },
      }));
    } catch (error: any) {
      console.error("Error loading transactions:", error);
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, transactions: false },
        error: {
          ...prevState.error,
          transactions: error.message || "Failed to load transactions",
        },
      }));
    }
  }, [state.user]);

  const refreshLeaderboard = useCallback(async () => {
    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, leaderboard: true },
        error: { ...prevState.error, leaderboard: null },
      }));

      // Call the leaderboard API
      const response = await leaderboardService.getLeaderboard(50);
      const leaderboardData = response.leaderboard || [];

      // Transform API data to frontend format
      const transformedLeaderboard = leaderboardData.map((entry: any) => ({
        rank: entry.rank,
        userId: entry.user_id.toString(),
        userName: entry.full_name || entry.username,
        userAvatar: "/placeholder-user.jpg", // Default avatar
        portfolioValue: entry.portfolio_value,
        totalReturn: entry.total_return,
        totalReturnPercent: entry.total_return_percent,
        investedValue: entry.invested_value,
        positionsValue: entry.positions_value,
        cashBalance: entry.cash_balance,
        activePositions: entry.active_positions,
      }));

      setState((prevState) => ({
        ...prevState,
        leaderboard: transformedLeaderboard,
        isLoading: { ...prevState.isLoading, leaderboard: false },
      }));
    } catch (error: any) {
      console.error("Error loading leaderboard:", error);
      setState((prevState) => ({
        ...prevState,
        leaderboard: [], // Empty array on error
        isLoading: { ...prevState.isLoading, leaderboard: false },
        error: {
          ...prevState.error,
          leaderboard: error.message || "Failed to load leaderboard",
        },
      }));
    }
  }, []);

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (authAPI.isAuthenticated()) {
        try {
          const userData = await userAPI.getCurrentUser();
          const user = apiUserToUser(userData);
          setState((prevState) => ({
            ...prevState,
            user,
          }));

          // Load initial data
          refreshStocks();
          refreshPortfolio();
          refreshTransactions();
          refreshLeaderboard();
        } catch (error) {
          console.error("Error loading user data:", error);
          // If token is invalid, clear it and redirect to login
          authAPI.logout();
          setState((prevState) => ({
            ...prevState,
            user: null,
          }));
          // Only redirect if we're not already on login/register pages
          if (
            typeof window !== "undefined" &&
            !window.location.pathname.includes("/login") &&
            !window.location.pathname.includes("/register")
          ) {
            window.location.href = "/login";
          }
        }
      } else {
        // Load real stock data even when not logged in
        refreshStocks();
        refreshLeaderboard();
      }
    };

    checkAuth();

    // Set up periodic stock price updates (every 5 minutes) - ONLY ONCE
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(() => {
      if (mountedRef.current) {
        console.log("Periodic stock refresh (every 2 minutes)");
        refreshStocks();
      }
    }, 120000); // 2 minutes for more frequent updates

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, []); // ✅ EMPTY DEPENDENCY ARRAY - run only once on mount

  const login = async (email: string, password: string) => {
    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, user: true },
        error: { ...prevState.error, user: null },
      }));

      // Call login API
      await authAPI.login(email, password);

      // Get user data
      const userData = await userAPI.getCurrentUser();
      const user = apiUserToUser(userData);

      setState((prevState) => ({
        ...prevState,
        user,
        isLoading: { ...prevState.isLoading, user: false },
      }));

      // Load initial data
      refreshStocks();
      refreshPortfolio();
      refreshTransactions();
      refreshLeaderboard();
    } catch (error: any) {
      console.error("Login failed:", error);
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, user: false },
        error: { ...prevState.error, user: error.message || "Login failed" },
      }));
      throw error;
    }
  };

  const logout = useCallback(() => {
    authAPI.logout();
    setState(initialState);
  }, []);

  const buyStock = useCallback(
    async (stockId: number, shares: number) => {
      try {
        setState((prevState) => ({
          ...prevState,
          isLoading: { ...prevState.isLoading, portfolio: true },
          error: { ...prevState.error, portfolio: null },
        }));

        // Call buy stock API
        await transactionAPI.buyStock(stockId, shares);

        // Refresh portfolio and transactions data
        await refreshPortfolio();
        await refreshTransactions();
      } catch (error: any) {
        console.error("Error buying stock:", error);
        setState((prevState) => ({
          ...prevState,
          isLoading: { ...prevState.isLoading, portfolio: false },
          error: {
            ...prevState.error,
            portfolio: error.message || "Failed to buy stock",
          },
        }));
        throw error;
      }
    },
    [refreshPortfolio, refreshTransactions]
  );

  const sellStock = useCallback(
    async (stockId: number, shares: number) => {
      try {
        setState((prevState) => ({
          ...prevState,
          isLoading: { ...prevState.isLoading, portfolio: true },
          error: { ...prevState.error, portfolio: null },
        }));

        // Call sell stock API
        await transactionAPI.sellStock(stockId, shares);

        // Refresh portfolio and transactions data
        await refreshPortfolio();
        await refreshTransactions();
      } catch (error: any) {
        console.error("Error selling stock:", error);
        setState((prevState) => ({
          ...prevState,
          isLoading: { ...prevState.isLoading, portfolio: false },
          error: {
            ...prevState.error,
            portfolio: error.message || "Failed to sell stock",
          },
        }));
        throw error;
      }
    },
    [refreshPortfolio, refreshTransactions]
  );

  const value = {
    ...state,
    login,
    logout,
    buyStock,
    sellStock,
    refreshStocks,
    refreshPortfolio,
    refreshTransactions,
    refreshLeaderboard,
    searchStocks,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export const useApp = () => {
  const context = useContext(AppContext);

  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }

  return context;
};
