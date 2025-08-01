import { jwtDecode } from "jwt-decode";

// Types for authentication
export interface User {
  id: string;
  username: string;
  email: string;
  balance?: number;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// Base API URL - should come from environment variable
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Auth service for handling authentication-related operations
export const AuthService = {
  // Login user and get tokens
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    try {
      const response = await fetch(`${API_URL}/auth/login-json`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();
      return data as AuthTokens;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  },

  // Register a new user
  async register(data: RegisterData): Promise<User> {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
      }

      return await response.json();
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    }
  },

  // Get the current user from token
  getCurrentUser(): User | null {
    if (typeof window === "undefined") {
      return null; // Not running in browser
    }

    try {
      const token = this.getToken();
      if (!token) return null;

      const decoded = jwtDecode<{
        sub: string;
        username: string;
        email: string;
        balance?: number;
        full_name?: string;
      }>(token);

      return {
        id: decoded.sub,
        username: decoded.username,
        email: decoded.email,
        balance: decoded.balance,
        full_name: decoded.full_name,
      };
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  },

  // Store token in localStorage (consistent with API service)
  setToken(token: string): void {
    if (typeof window === "undefined") return;

    localStorage.setItem("alphalearn_token", token);
    // Also set cookie for backwards compatibility
    document.cookie = `alphalearn_token=${token}; path=/; max-age=86400; SameSite=Strict`;
  },

  // Get token from localStorage (consistent with API service)
  getToken(): string | null {
    if (typeof window === "undefined") return null;

    return localStorage.getItem("alphalearn_token");
  },

  // Remove token from both localStorage and cookies
  removeToken(): void {
    if (typeof window === "undefined") return;

    localStorage.removeItem("alphalearn_token");
    document.cookie =
      "alphalearn_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT";
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  // Logout user
  logout(): void {
    this.removeToken();
  },
};

export default AuthService;
