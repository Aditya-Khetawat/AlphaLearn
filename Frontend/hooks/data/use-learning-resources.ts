"use client";

import { useState, useEffect, useCallback } from "react";
import { learningService } from "@/services/api";
import { LearningResource } from "@/types";

export function useLearningResources(
  initialCategory = "",
  initialDifficulty = ""
) {
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    category: initialCategory,
    difficulty: initialDifficulty,
  });

  const fetchResources = useCallback(
    async (category = filters.category, difficulty = filters.difficulty) => {
      try {
        setIsLoading(true);
        setError(null);

        // In a real app, this would call the API
        // For now, we'll simulate a delay and return mock data
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Mock learning resources
        const mockResources: LearningResource[] = [
          {
            id: "lr-1",
            title: "Introduction to Stock Markets",
            description:
              "Learn the basics of stock markets and how they operate.",
            category: "Stocks",
            difficulty: "Beginner",
            duration: "15 min",
            imageUrl: "/placeholder.jpg",
            url: "/learn/stocks-intro",
          },
          {
            id: "lr-2",
            title: "Understanding Market Orders",
            description:
              "Learn about different types of market orders and when to use them.",
            category: "Trading",
            difficulty: "Beginner",
            duration: "20 min",
            imageUrl: "/placeholder.jpg",
            url: "/learn/market-orders",
          },
          {
            id: "lr-3",
            title: "Technical Analysis Basics",
            description:
              "Introduction to technical analysis and chart patterns.",
            category: "Analysis",
            difficulty: "Intermediate",
            duration: "30 min",
            imageUrl: "/placeholder.jpg",
            url: "/learn/technical-analysis",
          },
          {
            id: "lr-4",
            title: "Fundamental Analysis",
            description:
              "Learn how to evaluate companies based on financial statements.",
            category: "Analysis",
            difficulty: "Intermediate",
            duration: "45 min",
            imageUrl: "/placeholder.jpg",
            url: "/learn/fundamental-analysis",
          },
          {
            id: "lr-5",
            title: "Portfolio Diversification Strategies",
            description:
              "Advanced techniques for building a diversified portfolio.",
            category: "Portfolio",
            difficulty: "Advanced",
            duration: "40 min",
            imageUrl: "/placeholder.jpg",
            url: "/learn/diversification",
          },
        ];

        // Filter resources based on category and difficulty if provided
        let filteredResources = [...mockResources];

        if (category) {
          filteredResources = filteredResources.filter(
            (resource) =>
              resource.category.toLowerCase() === category.toLowerCase()
          );
        }

        if (difficulty) {
          filteredResources = filteredResources.filter(
            (resource) =>
              resource.difficulty.toLowerCase() === difficulty.toLowerCase()
          );
        }

        setResources(filteredResources);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to fetch learning resources"
        );
        console.error("Error fetching learning resources:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [filters]
  );

  // Initial fetch
  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  // Update filters
  const updateFilters = useCallback(
    (newFilters: { category?: string; difficulty?: string }) => {
      const updatedFilters = {
        ...filters,
        ...newFilters,
      };

      setFilters(updatedFilters);
      fetchResources(updatedFilters.category, updatedFilters.difficulty);
    },
    [filters, fetchResources]
  );

  return {
    resources,
    isLoading,
    error,
    filters,
    updateFilters,
    refreshResources: fetchResources,
  };
}
