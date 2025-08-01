"use client";

import {
  createContext,
  useContext,
  ReactNode,
  useState,
  useEffect,
  useCallback,
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

import { supabase } from "@/lib/supabase-client";

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

  // Forward declarations for functions that reference each other
  const refreshStocks = useCallback(async () => {
    // Skip if user is not authenticated
    if (!authAPI.isAuthenticated()) {
      return;
    }

    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, stocks: true },
        error: { ...prevState.error, stocks: null },
      }));

      // Call stocks API
      const apiStocks: ApiStock[] = await stockAPI.getStocks();
      const stocks = apiStocks.map(apiStockToStock);

      setState((prevState) => ({
        ...prevState,
        stocks,
        isLoading: { ...prevState.isLoading, stocks: false },
      }));
    } catch (error: any) {
      console.error("Error loading stocks:", error);
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, stocks: false },
        error: {
          ...prevState.error,
          stocks: error.message || "Failed to load stocks",
        },
      }));
    }
  }, []);

  const refreshPortfolio = useCallback(async () => {
    // Skip if user is not authenticated
    if (!authAPI.isAuthenticated()) {
      return;
    }

    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, portfolio: true },
        error: { ...prevState.error, portfolio: null },
      }));

      // Call portfolio API
      const apiPortfolio: ApiPortfolio = await portfolioAPI.getPortfolio();

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
    // Skip if user is not authenticated
    if (!authAPI.isAuthenticated()) {
      return;
    }

    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, transactions: true },
        error: { ...prevState.error, transactions: null },
      }));

      // Call transactions history API
      const apiTransactions: ApiTransaction[] =
        await transactionAPI.getTransactionHistory();
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
  }, []);

  const refreshLeaderboard = useCallback(async () => {
    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, leaderboard: true },
        error: { ...prevState.error, leaderboard: null },
      }));

      // TODO: Implement real leaderboard API endpoint
      // For now, show empty leaderboard instead of fake users
      setState((prevState) => ({
        ...prevState,
        leaderboard: [], // Empty array until real backend API is implemented
        isLoading: { ...prevState.isLoading, leaderboard: false },
      }));
    } catch (error: any) {
      console.error("Error loading leaderboard:", error);
      setState((prevState) => ({
        ...prevState,
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
      try {
        // Check for existing Supabase session
        const { data } = await supabase.auth.getSession();

        if (data.session) {
          // Get user data using Supabase token
          const userData = await userAPI.getCurrentUser(
            data.session.access_token
          );
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
        } else if (authAPI.isAuthenticated()) {
          // Fallback to traditional token if for some reason we have legacy token
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
            authAPI.logout();
          }
        } else {
          // For development, load mock data until user logs in
          setState((prevState) => ({
            ...prevState,
            stocks: mockStocks,
            leaderboard: [], // Empty array until real backend API is implemented
          }));
        }
      } catch (error) {
        console.error("Session check error:", error);
      }
    };

    checkAuth();

    // Set up auth state change listener
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === "SIGNED_IN" && session) {
          try {
            const userData = await userAPI.getCurrentUser(session.access_token);
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
            console.error("Error fetching user data:", error);
          }
        } else if (event === "SIGNED_OUT") {
          setState(initialState);
        }
      }
    );

    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, [
    refreshLeaderboard,
    refreshPortfolio,
    refreshStocks,
    refreshTransactions,
  ]);

  const login = async (email: string, password: string) => {
    try {
      setState((prevState) => ({
        ...prevState,
        isLoading: { ...prevState.isLoading, user: true },
        error: { ...prevState.error, user: null },
      }));

      // Sign in with Supabase
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      // Call login API to sync with our backend
      await authAPI.login(email, password);

      // Get user data
      const userData = await userAPI.getCurrentUser(data.session?.access_token);
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

  const logout = useCallback(async () => {
    try {
      // Sign out from Supabase
      await supabase.auth.signOut();

      // Sign out from our API
      authAPI.logout();

      // Reset app state
      setState(initialState);
    } catch (error) {
      console.error("Logout error:", error);
    }
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
