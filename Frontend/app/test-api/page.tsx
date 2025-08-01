"use client";

import { useState, useCallback } from "react";
import { stockAPI } from "@/lib/api";

export default function TestAPIPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testStockSearch = useCallback(async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      console.log("Testing stock search with query:", query);
      const response = await stockAPI.searchStocks(query, 10);
      console.log("API Response:", response);
      setResults(response);
    } catch (err: any) {
      console.error("API Error:", err);
      setError(err.message || "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }, [query]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Stock API Test</h1>

      <div className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter stock query (e.g., RELIANCE)"
          className="border border-gray-300 rounded px-3 py-2 mr-2"
        />
        <button
          onClick={testStockSearch}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Loading..." : "Search Stocks"}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <strong>Success!</strong> Found {results.length} stocks
          <pre className="mt-2 text-sm">{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
