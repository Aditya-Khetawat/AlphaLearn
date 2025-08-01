"use client";

import { useEffect, useState } from "react";
import {
  TrendingUp,
  DollarSign,
  BarChart3,
  TrendingDown,
  Wallet,
  RefreshCw,
  Loader2,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { MainLayout } from "@/components/layout/main-layout";
import { useApp } from "@/context/app-context";

export default function PortfolioPage() {
  const { portfolio, user, isLoading, refreshPortfolio } = useApp();
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Refresh portfolio data on mount and when user changes
  useEffect(() => {
    if (user) {
      console.log(
        "Portfolio page mounted - refreshing portfolio data with latest prices"
      );
      refreshPortfolio().then(() => {
        setLastUpdated(new Date());
      });
    }
  }, [user, refreshPortfolio]);

  // Auto-refresh portfolio data every 2 minutes to keep prices updated
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      console.log("Auto-refreshing portfolio data for updated stock prices");
      refreshPortfolio().then(() => {
        setLastUpdated(new Date());
      });
    }, 120000); // 2 minutes

    return () => clearInterval(interval);
  }, [user, refreshPortfolio]);

  // Handle manual refresh
  const handleRefresh = async () => {
    await refreshPortfolio();
    setLastUpdated(new Date());
  };

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">Portfolio Overview</h2>
            <div className="space-y-1">
              <p className="text-muted-foreground">
                Track your investments and performance in Indian stocks.
              </p>
              {lastUpdated && (
                <p className="text-xs text-muted-foreground">
                  Prices last updated: {lastUpdated.toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>

          {/* Refresh Button */}
          <Button
            onClick={handleRefresh}
            disabled={isLoading.portfolio}
            variant="outline"
            size="sm"
          >
            {isLoading.portfolio ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Updating Prices...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Prices
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Portfolio Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        {/* Cash Balance */}
        <Card className="hover:bg-accent/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cash Balance</CardTitle>
            <Wallet className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{(portfolio?.cash || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Available for trading
            </p>
          </CardContent>
        </Card>

        {/* Total Invested */}
        <Card className="hover:bg-accent/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Invested
            </CardTitle>
            <DollarSign className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{(portfolio?.investedValue || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Amount invested in stocks
            </p>
          </CardContent>
        </Card>

        {/* Current Value */}
        <Card className="hover:bg-accent/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Value</CardTitle>
            <BarChart3 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{(portfolio?.totalValue || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Current market value of stocks
            </p>
          </CardContent>
        </Card>

        {/* Total P&L */}
        <Card className="hover:bg-accent/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Stock P&L</CardTitle>
            {(portfolio?.totalReturn || 0) >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${
                (portfolio?.totalReturn || 0) >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }`}
            >
              {(portfolio?.totalReturn || 0) >= 0 ? "+" : ""}₹
              {(portfolio?.totalReturn || 0).toLocaleString()}
            </div>
            <p
              className={`text-xs mt-1 flex items-center gap-1 ${
                (portfolio?.totalReturn || 0) >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }`}
            >
              {(portfolio?.totalReturn || 0) >= 0 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {(portfolio?.totalReturnPercent || 0) >= 0 ? "+" : ""}
              {(portfolio?.totalReturnPercent || 0).toFixed(2)}% on stocks
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Current Holdings
          </CardTitle>
          <CardDescription>
            Your active stock positions and their performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Avg Buy Price</TableHead>
                <TableHead>Current Price</TableHead>
                <TableHead>Total Value</TableHead>
                <TableHead>P&L</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {portfolio?.positions && portfolio.positions.length > 0 ? (
                portfolio.positions.map((position) => (
                  <TableRow
                    key={position.symbol}
                    className="hover:bg-accent/50"
                  >
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-xs font-semibold">
                            {position.symbol.slice(0, 2)}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{position.symbol}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{position.shares}</TableCell>
                    <TableCell>₹{position.averageCost.toFixed(2)}</TableCell>
                    <TableCell>₹{position.currentPrice.toFixed(2)}</TableCell>
                    <TableCell>₹{position.currentValue.toFixed(2)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span
                          className={`font-medium ${
                            position.totalReturn >= 0
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {position.totalReturn >= 0 ? "+" : ""}₹
                          {position.totalReturn.toFixed(2)}
                        </span>
                        <Badge
                          variant={
                            position.totalReturn >= 0
                              ? "default"
                              : "destructive"
                          }
                          className={
                            position.totalReturn >= 0
                              ? "bg-green-600 text-white"
                              : "bg-red-600 text-white"
                          }
                        >
                          {position.totalReturn >= 0 ? "+" : ""}
                          {position.totalReturnPercent.toFixed(2)}%
                        </Badge>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="text-center py-8 text-muted-foreground"
                  >
                    {!user
                      ? "Please log in to view your portfolio."
                      : isLoading.portfolio && !portfolio
                      ? "Loading positions..."
                      : "No positions yet. Start trading to see your holdings here."}
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
