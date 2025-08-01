// API endpoints
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

// For real implementation, you'd replace these with actual API calls
// This is a simple structure for demonstration purposes

// Helper for making API requests
async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Add authorization header if user is logged in
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  const fullUrl = `${API_URL}${endpoint}`;
  console.log(`API Request: ${options.method || "GET"} ${fullUrl}`);

  const response = await fetch(fullUrl, {
    ...options,
    credentials: "include", // Enable cookies/credentials
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    console.error(
      `API Error: ${response.status} ${response.statusText} for ${fullUrl}`
    );
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || `API request failed with status ${response.status}`
    );
  }

  // For endpoints that don't return JSON, just return the response
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return await response.json();
  }

  return response;
}

// Authentication Service
export const authService = {
  login: async (email: string, password: string) => {
    return fetchApi("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email, // FastAPI OAuth expects 'username'
        password,
        grant_type: "password",
      }),
    });
  },

  register: async (
    username: string,
    email: string,
    password: string,
    full_name?: string
  ) => {
    return fetchApi("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password, full_name }),
    });
  },

  logout: async () => {
    localStorage.removeItem("token");
    return fetchApi("/auth/logout/", { method: "POST" });
  },

  getCurrentUser: async () => {
    return fetchApi("/users/me/");
  },
};

// Stock Service
export const stockService = {
  getStocks: async (query = "", limit = 20) => {
    const params = new URLSearchParams();
    if (query) params.append("search", query);
    params.append("limit", limit.toString());
    return fetchApi(`/stocks/?${params.toString()}`);
  },

  getStockDetails: async (symbol: string) => {
    return fetchApi(`/stocks/symbol/${symbol}`);
  },

  getStockPriceHistory: async (
    symbol: string,
    timeframe = "1d",
    interval = "1d"
  ) => {
    try {
      return await fetchApi(
        `/stocks/${symbol}/history?timeframe=${timeframe}&interval=${interval}`
      );
    } catch (error: any) {
      console.error(`Failed to fetch history for ${symbol}:`, error);
      // Return empty data in the same format as successful response
      if (error.message.includes("404")) {
        console.warn(
          `History endpoint not implemented for ${symbol}, returning empty data`
        );
        return { symbol, timeframe, interval, data: [], count: 0 };
      }
      throw error;
    }
  },
};

// Portfolio Service
export const portfolioService = {
  getPortfolio: async () => {
    return fetchApi("/portfolios/me/");
  },

  buyStock: async (symbol: string, shares: number, price: number) => {
    return fetchApi("/portfolios/buy/", {
      method: "POST",
      body: JSON.stringify({ symbol, shares, price }),
    });
  },

  sellStock: async (symbol: string, shares: number, price: number) => {
    return fetchApi("/portfolios/sell/", {
      method: "POST",
      body: JSON.stringify({ symbol, shares, price }),
    });
  },
};

// Transaction Service
export const transactionService = {
  getTransactions: async (limit = 20, offset = 0) => {
    return fetchApi(`/transactions/history/?skip=${offset}&limit=${limit}`);
  },

  getTransactionDetails: async (id: string) => {
    return fetchApi(`/transactions/${id}/`);
  },
};

// Leaderboard Service
export const leaderboardService = {
  getLeaderboard: async (limit = 50) => {
    return fetchApi(`/leaderboard/?limit=${limit}`);
  },

  getUserRank: async (userId: string) => {
    return fetchApi(`/leaderboard/user/${userId}`);
  },
};

// Learning Resources Service
export const learningService = {
  getResources: async (category = "", difficulty = "") => {
    let url = "/learning";
    const params = [];

    if (category) params.push(`category=${category}`);
    if (difficulty) params.push(`difficulty=${difficulty}`);

    if (params.length) url += `?${params.join("&")}`;

    return fetchApi(url);
  },

  getResourceDetails: async (id: string) => {
    return fetchApi(`/learning/${id}`);
  },
};
