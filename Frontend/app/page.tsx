"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { MainLayout } from "@/components/layout/main-layout";
import { useApp } from "@/context/app-context";

export default function Dashboard() {
  const {
    user,
    portfolio,
    stocks,
    transactions,
    isLoading,
    refreshStocks,
    refreshPortfolio,
    refreshTransactions,
  } = useApp();

  // State to track if we've ever loaded transactions to prevent flickering
  const [hasLoadedTransactions, setHasLoadedTransactions] = useState(false);

  // State to track client-side mounting to prevent hydration errors
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  useEffect(() => {
    // Fetch initial data on mount only
    refreshStocks();
    refreshPortfolio();
    refreshTransactions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Track when transactions have been loaded
  useEffect(() => {
    if (transactions.length > 0 || (!isLoading.transactions && user)) {
      setHasLoadedTransactions(true);
    }
  }, [transactions.length, isLoading.transactions, user]);

  // Format transaction timestamp for display
  const formatTransactionTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 1) {
      return "Just now";
    } else if (diffInHours < 24) {
      return `${diffInHours} hour${diffInHours > 1 ? "s" : ""} ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} day${diffInDays > 1 ? "s" : ""} ago`;
    }
  };

  // Get recent transactions (last 5) with memoization to prevent flickering
  const recentTransactions = useMemo(() => {
    return transactions.slice(0, 5);
  }, [transactions]);

  // Memoized loading state for transactions to prevent flickering
  const showTransactionLoading = useMemo(() => {
    // Only show loading if user is logged in, currently loading, and has never loaded transactions
    return user && isLoading.transactions && transactions.length === 0;
  }, [user, isLoading.transactions, transactions.length]);

  // More stable loading state that prevents rapid state changes
  const transactionDisplayState = useMemo(() => {
    if (!user) {
      return "no-user";
    }
    if (recentTransactions.length > 0) {
      return "has-transactions";
    }
    // Only show loading if we haven't loaded transactions yet and are currently loading
    if (isLoading.transactions && !hasLoadedTransactions) {
      return "loading";
    }
    return "no-transactions";
  }, [
    user,
    recentTransactions.length,
    isLoading.transactions,
    hasLoadedTransactions,
  ]);

  // Memoized balance to prevent flickering - consistent with main layout
  const userBalance = useMemo(() => {
    // Priority: portfolio cash > user balance > default 100000
    if (portfolio?.cash !== undefined && portfolio.cash !== null) {
      return portfolio.cash;
    }
    return user?.balance ?? 100000;
  }, [user?.balance, portfolio?.cash]);

  return (
    <MainLayout>
      {/* Welcome Message */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">
          Welcome, {user?.name || "User"}! 👋
        </h2>
        <p className="text-muted-foreground">
          {portfolio?.positions?.length
            ? `Track your investments in the Indian stock market.`
            : hasMounted
            ? `Start investing your ₹${userBalance.toLocaleString(
                "en-IN"
              )} in the Indian stock market.`
            : `Start investing your ₹... in the Indian stock market.`}
        </p>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {/* Account Balance */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Account Balance
            </CardTitle>
            <DollarSign className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{hasMounted ? userBalance.toLocaleString("en-IN") : "..."}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Available for trading
            </p>
          </CardContent>
        </Card>

        {/* Portfolio Value */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Invested Value
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{portfolio?.investedValue?.toFixed(2) || "0.00"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {portfolio?.positions?.length
                ? `Across ${portfolio.positions.length} positions`
                : "No investments yet"}
            </p>
          </CardContent>
        </Card>

        {/* Total Return */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Return</CardTitle>
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
              ₹{portfolio?.totalReturn.toFixed(2) || "0.00"}
            </div>
            <p
              className={`text-xs mt-1 flex items-center gap-1 ${
                (portfolio?.totalReturnPercent || 0) >= 0
                  ? "text-green-500"
                  : "text-red-500"
              }`}
            >
              {(portfolio?.totalReturnPercent || 0) >= 0 ? (
                <TrendingUp className="h-3 w-3" />
              ) : (
                <TrendingDown className="h-3 w-3" />
              )}
              {(portfolio?.totalReturnPercent || 0).toFixed(2)}% overall
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Top Holdings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Your Holdings
          </CardTitle>
          <CardDescription>Your current positions</CardDescription>
        </CardHeader>
        <CardContent>
          {!user ? (
            // User not logged in - show start trading message
            <div className="text-center py-4 text-muted-foreground">
              You have ₹
              {hasMounted ? userBalance.toLocaleString("en-IN") : "..."} to
              invest! Head to the Trade section to start building your portfolio
              with Indian stocks.
              <div className="mt-4">
                <Button asChild>
                  <Link href="/trade">Start Trading</Link>
                </Button>
              </div>
            </div>
          ) : isLoading.portfolio && !portfolio ? (
            // User logged in but portfolio is loading for the first time
            <div className="text-center py-4">Loading positions...</div>
          ) : portfolio?.positions && portfolio.positions.length > 0 ? (
            <div className="space-y-4">
              {portfolio.positions.map((position) => (
                <div
                  key={position.symbol}
                  className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-sm font-semibold">
                        {position.symbol.slice(0, 2)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{position.symbol}</p>
                      <p className="text-sm text-muted-foreground">
                        {position.shares} shares
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      ₹{position.currentValue.toFixed(2)}
                    </p>
                    <Badge
                      variant={
                        position.totalReturn >= 0 ? "default" : "destructive"
                      }
                      className={
                        position.totalReturn >= 0
                          ? "bg-green-600"
                          : "bg-red-600"
                      }
                    >
                      {position.totalReturn >= 0 ? "+" : ""}
                      {position.totalReturnPercent.toFixed(2)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              You have ₹
              {hasMounted ? userBalance.toLocaleString("en-IN") : "..."} to
              invest! Head to the Trade section to start building your portfolio
              with Indian stocks.
              <div className="mt-4">
                <Button asChild>
                  <Link href="/trade">Start Trading</Link>
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
          <CardDescription>Your latest trades and transactions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Shares</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactionDisplayState === "has-transactions" ? (
                recentTransactions.map((transaction) => (
                  <TableRow key={transaction.id}>
                    <TableCell className="font-medium">
                      {transaction.symbol}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          transaction.type === "BUY" ? "default" : "destructive"
                        }
                        className={
                          transaction.type === "BUY"
                            ? "bg-green-600"
                            : "bg-red-600"
                        }
                      >
                        {transaction.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{transaction.shares}</TableCell>
                    <TableCell>
                      ₹
                      {hasMounted
                        ? transaction.price.toLocaleString("en-IN")
                        : "..."}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatTransactionTime(transaction.timestamp)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className="border-green-600 text-green-500"
                      >
                        Completed
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="text-center text-muted-foreground py-8"
                  >
                    {transactionDisplayState === "loading"
                      ? "Loading transactions..."
                      : "No recent transactions"}
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
