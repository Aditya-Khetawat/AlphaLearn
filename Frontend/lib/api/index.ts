/**
 * API client for AlphaLearn backend
 */

// API Error interface
interface APIError extends Error {
  status: number;
  data?: any;
}

// API base URL - will use environment variable or default to localhost during development
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Default headers for all requests
const defaultHeaders = {
  "Content-Type": "application/json",
};

// Helper to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        detail:
          response.status === 500
            ? "Server is currently unavailable. Please try again later."
            : response.statusText,
      };
    }

    const error = new Error(
      errorData.detail || response.statusText
    ) as APIError;
    error.status = response.status;
    error.data = errorData;
    throw error;
  }

  try {
    return await response.json();
  } catch {
    return {}; // Return empty object if JSON parsing fails
  }
};

/**
 * Store auth token in localStorage and cookie for middleware
 */
const setToken = (token: string) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("alphalearn_token", token);
    // Also set cookie for middleware to read
    document.cookie = `alphalearn_token=${token}; path=/; max-age=${
      7 * 24 * 60 * 60
    }; SameSite=Lax`;
  }
};

/**
 * Get auth token from localStorage
 */
const getToken = (): string | null => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("alphalearn_token");
  }
  return null;
};

/**
 * Remove auth token from localStorage and cookie
 */
const removeToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("alphalearn_token");
    // Also remove cookie
    document.cookie = `alphalearn_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
  }
};

/**
 * Get auth headers with token if available
 */
const getAuthHeaders = (token?: string) => {
  const storedToken = token || getToken();
  return storedToken
    ? { Authorization: `Bearer ${storedToken}` }
    : ({} as Record<string, string>);
};

/**
 * Authentication API calls
 */
export const authAPI = {
  /**
   * Login with email and password
   */
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    // FastAPI's OAuth2 endpoint expects username field (even if we use email)
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    const data = await handleResponse(response);
    setToken(data.access_token);
    return data;
  },

  /**
   * Register a new user
   */
  register: async (userData: {
    email: string;
    username: string;
    full_name?: string;
    password: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: defaultHeaders,
      body: JSON.stringify(userData),
    });

    return handleResponse(response);
  },

  /**
   * Logout the current user
   */
  logout: () => {
    removeToken();
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!getToken();
  },
};

/**
 * User API calls
 */
export const userAPI = {
  /**
   * Get current user profile
   */
  getCurrentUser: async (token?: string) => {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: {
        ...defaultHeaders,
        ...getAuthHeaders(token),
      },
    });

    return handleResponse(response);
  },

  /**
   * Update user profile
   */
  updateUser: async (userData: {
    email?: string;
    full_name?: string;
    password?: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: "PUT",
      headers: {
        ...defaultHeaders,
        ...getAuthHeaders(),
      },
      body: JSON.stringify(userData),
    });

    return handleResponse(response);
  },
};

/**
 * Stock API calls
 */
export const stockAPI = {
  /**
   * Get list of stocks
   */
  getStocks: async (params?: {
    skip?: number;
    limit?: number;
    exchange?: string;
    sector?: string;
  }) => {
    try {
      const urlParams = new URLSearchParams();

      if (params?.skip) urlParams.append("skip", params.skip.toString());
      if (params?.limit) urlParams.append("limit", params.limit.toString());
      if (params?.exchange) urlParams.append("exchange", params.exchange);
      if (params?.sector) urlParams.append("sector", params.sector);

      const query = urlParams.toString() ? `?${urlParams.toString()}` : "";

      const response = await fetch(`${API_BASE_URL}/stocks${query}`, {
        headers: defaultHeaders,
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });

      return handleResponse(response);
    } catch (error) {
      console.warn(
        "Failed to fetch stocks from API, using fallback data:",
        error
      );
      // Return fallback data if API fails
      return [
        {
          id: 1,
          symbol: "TCS",
          name: "Tata Consultancy Services Limited",
          current_price: 3250.5,
          previous_close: 3200.0,
          price_change: 50.5,
          price_change_percent: 1.58,
          exchange: "NSE",
          sector: "Information Technology",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
        {
          id: 2,
          symbol: "RELIANCE",
          name: "Reliance Industries Limited",
          current_price: 2845.75,
          previous_close: 2880.0,
          price_change: -34.25,
          price_change_percent: -1.19,
          exchange: "NSE",
          sector: "Energy",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
        {
          id: 3,
          symbol: "HDFCBANK",
          name: "HDFC Bank Limited",
          current_price: 1650.2,
          previous_close: 1630.5,
          price_change: 19.7,
          price_change_percent: 1.21,
          exchange: "NSE",
          sector: "Financial Services",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
      ];
    }
  },

  /**
   * Get stock by ID
   */
  getStockById: async (id: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/stocks/${id}`, {
        headers: defaultHeaders,
        signal: AbortSignal.timeout(10000),
      });

      return handleResponse(response);
    } catch (error) {
      console.warn(
        `Failed to fetch stock ${id} from API, using fallback data:`,
        error
      );
      // Return fallback stock data
      const fallbackStocks: { [key: number]: any } = {
        1: {
          id: 1,
          symbol: "TCS",
          name: "Tata Consultancy Services Limited",
          current_price: 3250.5,
          previous_close: 3200.0,
          price_change: 50.5,
          price_change_percent: 1.58,
          exchange: "NSE",
          sector: "Information Technology",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
        2: {
          id: 2,
          symbol: "RELIANCE",
          name: "Reliance Industries Limited",
          current_price: 2845.75,
          previous_close: 2880.0,
          price_change: -34.25,
          price_change_percent: -1.19,
          exchange: "NSE",
          sector: "Energy",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
      };

      if (fallbackStocks[id]) {
        return fallbackStocks[id];
      } else {
        throw new Error("Stock not found");
      }
    }
  },

  /**
   * Search stocks
   */
  searchStocks: async (query: string, limit: number = 10) => {
    try {
      const urlParams = new URLSearchParams({
        query,
        limit: limit.toString(),
      });

      const response = await fetch(
        `${API_BASE_URL}/stocks/search?${urlParams.toString()}`,
        {
          headers: defaultHeaders,
          signal: AbortSignal.timeout(10000),
        }
      );

      return handleResponse(response);
    } catch (error) {
      console.warn(
        "Failed to search stocks from API, using fallback data:",
        error
      );
      // Return filtered fallback data based on search query
      const fallbackStocks = [
        {
          id: 1,
          symbol: "TCS",
          name: "Tata Consultancy Services Limited",
          current_price: 3250.5,
          previous_close: 3200.0,
          price_change: 50.5,
          price_change_percent: 1.58,
          exchange: "NSE",
          sector: "Information Technology",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
        {
          id: 2,
          symbol: "RELIANCE",
          name: "Reliance Industries Limited",
          current_price: 2845.75,
          previous_close: 2880.0,
          price_change: -34.25,
          price_change_percent: -1.19,
          exchange: "NSE",
          sector: "Energy",
          is_active: true,
          last_updated: new Date().toISOString(),
        },
      ];

      const queryLower = query.toLowerCase();
      const filtered = fallbackStocks.filter(
        (stock) =>
          stock.symbol.toLowerCase().includes(queryLower) ||
          stock.name.toLowerCase().includes(queryLower)
      );

      return filtered.length > 0 ? filtered : fallbackStocks.slice(0, limit);
    }
  },

  /**
   * Get historical data for a stock
   */
  getHistoricalData: async (
    symbol: string,
    period: string = "1D",
    interval: string = "5m"
  ) => {
    const urlParams = new URLSearchParams({
      period,
      interval,
    });

    const response = await fetch(
      `${API_BASE_URL}/stocks/${symbol}/historical?${urlParams.toString()}`,
      {
        headers: {
          ...defaultHeaders,
          ...getAuthHeaders(),
        },
      }
    );

    return handleResponse(response);
  },
};

/**
 * Portfolio API calls
 */
export const portfolioAPI = {
  /**
   * Get user's portfolio
   */
  getPortfolio: async (token?: string) => {
    const response = await fetch(`${API_BASE_URL}/portfolios/me`, {
      headers: {
        ...defaultHeaders,
        ...getAuthHeaders(token),
      },
    });

    return handleResponse(response);
  },
};

/**
 * Transaction API calls
 */
export const transactionAPI = {
  /**
   * Buy stock
   */
  buyStock: async (stockId: number, shares: number) => {
    // Check if user is authenticated before making the request
    const token = getToken();
    if (!token) {
      throw new Error(
        "You must be logged in to buy stocks. Please log in first."
      );
    }

    const response = await fetch(`${API_BASE_URL}/transactions/buy`, {
      method: "POST",
      headers: {
        ...defaultHeaders,
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        stock_id: stockId,
        shares,
      }),
    });

    return handleResponse(response);
  },

  /**
   * Sell stock
   */
  sellStock: async (stockId: number, shares: number) => {
    // Check if user is authenticated before making the request
    const token = getToken();
    if (!token) {
      throw new Error(
        "You must be logged in to sell stocks. Please log in first."
      );
    }

    const response = await fetch(`${API_BASE_URL}/transactions/sell`, {
      method: "POST",
      headers: {
        ...defaultHeaders,
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        stock_id: stockId,
        shares,
      }),
    });

    return handleResponse(response);
  },

  /**
   * Get transaction history
   */
  getTransactionHistory: async (skip: number = 0, limit: number = 100) => {
    const urlParams = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const response = await fetch(
      `${API_BASE_URL}/transactions/history?${urlParams.toString()}`,
      {
        headers: {
          ...defaultHeaders,
          ...getAuthHeaders(),
        },
      }
    );

    return handleResponse(response);
  },
};
