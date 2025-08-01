"use client";

import { useState, useEffect, useMemo } from "react";
import { TrendingUp, BarChart3, Activity, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MainLayout } from "@/components/layout/main-layout";
import { StockChart } from "@/components/charts/stock-chart";
import { useApp } from "@/context/app-context";
import { useToast } from "@/components/ui/use-toast";
import { Stock } from "@/types";

export default function TradePage() {
  const {
    user,
    stocks,
    transactions,
    buyStock,
    sellStock,
    isLoading,
    searchStocks,
  } = useApp();
  const { toast } = useToast();
  const [selectedStock, setSelectedStock] = useState("");
  const [selectedStockCache, setSelectedStockCache] = useState<Stock | null>(
    null
  );
  const [quantity, setQuantity] = useState("");
  const [orderType, setOrderType] = useState("buy");
  const [stockSearchQuery, setStockSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(stocks);
  const [isSearching, setIsSearching] = useState(false);

  // State to track if we've ever loaded transactions to prevent flickering
  const [hasLoadedTransactions, setHasLoadedTransactions] = useState(false);

  // Get the selected stock object - use cached data for instant access, fallback to search
  const selectedStockData = useMemo(() => {
    if (!selectedStock) return null;

    // Use cached data if available and symbol matches
    if (selectedStockCache && selectedStockCache.symbol === selectedStock) {
      return selectedStockCache;
    }

    // First try to find in search results
    let stock = searchResults.find((stock) => stock.symbol === selectedStock);

    // If not found in search results, look in main stocks array
    if (!stock) {
      stock = stocks.find((stock) => stock.symbol === selectedStock);
    }

    return stock || null;
  }, [selectedStock, selectedStockCache, searchResults, stocks]);

  // Get recent transactions (last 10) with memoization to prevent flickering
  const recentOrders = useMemo(() => {
    return transactions.slice(0, 10);
  }, [transactions]);

  // Track when transactions have been loaded
  useEffect(() => {
    if (transactions.length > 0 || (!isLoading.transactions && user)) {
      setHasLoadedTransactions(true);
    }
  }, [transactions.length, isLoading.transactions, user]);

  // More stable loading state that prevents rapid state changes
  const ordersDisplayState = useMemo(() => {
    if (!user) {
      return "no-user";
    }
    if (recentOrders.length > 0) {
      return "has-orders";
    }
    // Only show loading if we haven't loaded transactions yet and are currently loading
    if (isLoading.transactions && !hasLoadedTransactions) {
      return "loading";
    }
    return "no-orders";
  }, [
    user,
    recentOrders.length,
    isLoading.transactions,
    hasLoadedTransactions,
  ]);

  // Update search results when stocks change
  useEffect(() => {
    if (!stockSearchQuery) {
      setSearchResults(stocks);
    }
  }, [stocks, stockSearchQuery]);

  // Clear cache when selectedStock is cleared
  useEffect(() => {
    if (!selectedStock) {
      setSelectedStockCache(null);
    }
  }, [selectedStock]);

  // Handle stock search with debounce
  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (stockSearchQuery) {
        handleStockSearch(stockSearchQuery);
      }
    }, 300); // 300ms delay

    return () => clearTimeout(delayedSearch);
  }, [stockSearchQuery]);

  // Handle stock search
  const handleStockSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults(stocks);
      return;
    }

    setIsSearching(true);
    try {
      const results = await searchStocks(query);
      setSearchResults(results);
    } catch (error) {
      console.error("Error searching stocks:", error);
      // Fallback to local filtering
      const filteredStocks = stocks.filter(
        (stock) =>
          stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
          stock.name.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(filteredStocks);
    } finally {
      setIsSearching(false);
    }
  };

  const handleTrade = async () => {
    if (!selectedStock || !quantity || !selectedStockData) {
      toast({
        title: "Invalid Order",
        description: "Please select a stock and enter quantity",
        variant: "destructive",
      });
      return;
    }

    // Check authentication status
    if (!user) {
      toast({
        title: "Authentication Required",
        description:
          "You must be logged in to trade stocks. Redirecting to login...",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
      return;
    }

    try {
      const shares = parseInt(quantity);
      const totalValue = shares * selectedStockData.currentPrice;

      if (orderType === "buy") {
        await buyStock(selectedStockData.id, shares);
        toast({
          title: "🎉 Purchase Successful!",
          description: `Successfully bought ${shares} shares of ${selectedStock} at ₹${selectedStockData.currentPrice.toLocaleString()} each. Total: ₹${totalValue.toLocaleString()}`,
          variant: "default",
        });
      } else {
        await sellStock(selectedStockData.id, shares);
        toast({
          title: "🎉 Sale Successful!",
          description: `Successfully sold ${shares} shares of ${selectedStock} at ₹${selectedStockData.currentPrice.toLocaleString()} each. Total: ₹${totalValue.toLocaleString()}`,
          variant: "default",
        });
      }

      // Reset form
      setSelectedStock("");
      setQuantity("");
    } catch (error: any) {
      console.error("Trade error:", error);

      // Check if it's an authentication error
      if (error.message && error.message.includes("logged in")) {
        toast({
          title: "❌ Authentication Error",
          description: `${error.message}. Redirecting to login page...`,
          variant: "destructive",
        });
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        toast({
          title: "❌ Trade Failed",
          description:
            error.message || "An unexpected error occurred during the trade",
          variant: "destructive",
        });
      }
    }
  };

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Trade Stocks</h2>
        <p className="text-muted-foreground">
          Buy and sell stocks with real-time market data.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Trading Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Place Order
            </CardTitle>
            <CardDescription>
              Select a stock and place your trade order
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Stock Search */}
            <div className="space-y-2">
              <Label htmlFor="stock-search">Search & Select Stock</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="stock-search"
                  placeholder="Search by symbol or company name..."
                  value={stockSearchQuery}
                  onChange={(e) => {
                    setStockSearchQuery(e.target.value);
                    // Clear selection when user starts typing to search for a different stock
                    if (e.target.value && selectedStock) {
                      setSelectedStock("");
                      setSelectedStockCache(null);
                    }
                  }}
                  className="pl-10"
                />

                {/* Seamless Search Results Dropdown */}
                {stockSearchQuery && (
                  <div className="absolute z-50 w-full mt-1 border rounded-lg bg-background shadow-lg max-h-60 overflow-y-auto">
                    {isSearching ? (
                      <div className="p-4 text-center text-muted-foreground">
                        <div className="flex items-center justify-center gap-2">
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
                          Searching...
                        </div>
                      </div>
                    ) : searchResults.length === 0 ? (
                      <div className="p-4 text-center text-muted-foreground">
                        No stocks found for "{stockSearchQuery}"
                      </div>
                    ) : (
                      <div className="p-2">
                        <div className="text-xs text-muted-foreground mb-2 px-2">
                          {searchResults.length} stocks found
                        </div>
                        {searchResults.map((stock) => (
                          <div
                            key={stock.symbol}
                            onClick={() => {
                              setSelectedStock(stock.symbol);
                              setSelectedStockCache(stock); // Cache the stock data for instant access
                              setStockSearchQuery(""); // Clear search after selection
                            }}
                            className={`p-3 rounded-lg cursor-pointer hover:bg-accent transition-colors ${
                              selectedStock === stock.symbol ? "bg-accent" : ""
                            }`}
                          >
                            <div className="flex justify-between items-center">
                              <div className="flex flex-col">
                                <span className="font-medium">
                                  {stock.symbol}
                                </span>
                                <span className="text-sm text-muted-foreground">
                                  {stock.name}
                                </span>
                              </div>
                              <div className="text-right">
                                <div className="font-medium">
                                  ₹{stock.currentPrice.toFixed(2)}
                                </div>
                                <div
                                  className={`text-xs ${
                                    stock.change >= 0
                                      ? "text-green-600"
                                      : "text-red-600"
                                  }`}
                                >
                                  {stock.change >= 0 ? "+" : ""}
                                  {stock.changePercent.toFixed(2)}%
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Selected Stock Info */}
            {selectedStockData && (
              <div className="p-4 border rounded-lg bg-muted/50">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">
                      {selectedStockData.symbol}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedStockData.name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold">
                      ₹{selectedStockData.currentPrice.toFixed(2)}
                    </p>
                    <p
                      className={`text-sm ${
                        selectedStockData.change >= 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {selectedStockData.change >= 0 ? "+" : ""}₹
                      {selectedStockData.change.toFixed(2)} (
                      {selectedStockData.changePercent.toFixed(2)}%)
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Order Type Toggle */}
            <div className="space-y-2">
              <Label>Order Type</Label>
              <Tabs
                value={orderType}
                onValueChange={setOrderType}
                className="w-full"
              >
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger
                    value="buy"
                    className="data-[state=active]:bg-green-600 data-[state=active]:text-white"
                  >
                    Buy
                  </TabsTrigger>
                  <TabsTrigger
                    value="sell"
                    className="data-[state=active]:bg-red-600 data-[state=active]:text-white"
                  >
                    Sell
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            {/* Quantity Input */}
            <div className="space-y-2">
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                placeholder="Enter number of shares"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>

            {/* Current Price Display */}
            {selectedStockData && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Current Price:</span>
                  <span className="font-semibold">
                    ₹{selectedStockData.currentPrice.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-muted-foreground">
                    Estimated Total:
                  </span>
                  <span className="font-semibold">
                    ₹
                    {quantity
                      ? (
                          Number.parseFloat(quantity) *
                          selectedStockData.currentPrice
                        ).toFixed(2)
                      : "0.00"}
                  </span>
                </div>
              </div>
            )}

            {/* Authentication Check & Trade Button */}
            {!user ? (
              <div className="space-y-3">
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-sm text-amber-800 mb-2">
                    🔒 You need to be logged in to trade stocks
                  </p>
                  <p className="text-xs text-amber-600">
                    Please log in to buy and sell stocks with real money
                    simulation.
                  </p>
                </div>
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => (window.location.href = "/login")}
                >
                  Go to Login
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleTrade}
                disabled={!selectedStock || !quantity}
                className={`w-full ${
                  orderType === "buy"
                    ? "bg-green-600 hover:bg-green-700"
                    : "bg-red-600 hover:bg-red-700"
                } disabled:opacity-50`}
              >
                {orderType === "buy" ? "Buy" : "Sell"}{" "}
                {selectedStock || "Stock"}
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Real-time Price Chart */}
        {selectedStockData ? (
          <StockChart
            symbol={selectedStockData.symbol}
            currentPrice={selectedStockData.currentPrice}
            change={selectedStockData.change}
            changePercent={selectedStockData.changePercent}
          />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Price Chart
              </CardTitle>
              <CardDescription>
                Select a stock to view its real-time chart
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    Select a stock to view its live price chart
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Orders
          </CardTitle>
          <CardDescription>
            Your latest trade orders and their status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ordersDisplayState === "has-orders" ? (
                recentOrders.map((order, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {order.symbol}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          order.type === "BUY" ? "default" : "destructive"
                        }
                        className={
                          order.type === "BUY"
                            ? "bg-green-600 hover:bg-green-700"
                            : "bg-red-600 hover:bg-red-700"
                        }
                      >
                        {order.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{order.shares}</TableCell>
                    <TableCell>₹{order.price.toFixed(2)}</TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className="border-green-600 text-green-500"
                      >
                        completed
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(order.timestamp).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="text-center py-8 text-muted-foreground"
                  >
                    {ordersDisplayState === "loading"
                      ? "Loading transactions..."
                      : "No recent trades yet. Start trading to see your order history here."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
