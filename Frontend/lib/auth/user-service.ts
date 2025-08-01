// User API functions

import AuthService from "./auth";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  balance: number;
  created_at: string;
  updated_at: string;
}

export const UserService = {
  // Get current user profile
  async getCurrentUser(): Promise<UserProfile> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to get user profile");
      }

      return await response.json();
    } catch (error) {
      console.error("Get user profile error:", error);
      throw error;
    }
  },

  // Update user profile
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const token = AuthService.getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(`${API_URL}/users/me`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to update profile");
      }

      return await response.json();
    } catch (error) {
      console.error("Update profile error:", error);
      throw error;
    }
  },
};

export default UserService;
