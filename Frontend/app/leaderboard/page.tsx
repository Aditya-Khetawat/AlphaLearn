"use client";

import { useEffect, useState } from "react";
import {
  Trophy,
  Medal,
  Award,
  Users,
  Wifi,
  WifiOff,
  RotateCcw,
  Loader2,
  RefreshCw,
} from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
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
import { useLeaderboardWebSocket } from "@/hooks/useLeaderboardWebSocket";

function getRankBadge(rank: number) {
  switch (rank) {
    case 1:
      return (
        <Badge className="bg-yellow-600 hover:bg-yellow-700 text-white flex items-center gap-1">
          <Trophy className="h-3 w-3" />
          Gold
        </Badge>
      );
    case 2:
      return (
        <Badge className="bg-gray-400 hover:bg-gray-500 text-white flex items-center gap-1">
          <Medal className="h-3 w-3" />
          Silver
        </Badge>
      );
    case 3:
      return (
        <Badge className="bg-amber-600 hover:bg-amber-700 text-white flex items-center gap-1">
          <Award className="h-3 w-3" />
          Bronze
        </Badge>
      );
    default:
      return <span className="text-muted-foreground font-medium">#{rank}</span>;
  }
}

export default function LeaderboardPage() {
  const {
    isLoading,
    refreshLeaderboard,
    leaderboard: restLeaderboard,
  } = useApp();
  const {
    leaderboard: wsLeaderboard,
    isConnected,
    error: wsError,
    reconnect,
  } = useLeaderboardWebSocket();

  const [useWebSocket, setUseWebSocket] = useState(true);

  // Fallback to REST API if WebSocket fails
  useEffect(() => {
    if (wsError && useWebSocket) {
      console.warn("WebSocket failed, falling back to REST API");
      setUseWebSocket(false);
      refreshLeaderboard();
    }
  }, [wsError, useWebSocket, refreshLeaderboard]);

  // Load REST API data on mount if not using WebSocket
  useEffect(() => {
    if (!useWebSocket || (!isConnected && !wsError)) {
      refreshLeaderboard();
    }
  }, [useWebSocket, isConnected, wsError, refreshLeaderboard]);

  // Use WebSocket data if connected, otherwise fall back to REST API data
  const displayLeaderboard =
    useWebSocket && isConnected ? wsLeaderboard : restLeaderboard;
  const showLoading = useWebSocket
    ? !isConnected && !wsError
    : isLoading.leaderboard;

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Trophy className="h-8 w-8 text-yellow-500" />
              Top Traders
            </h2>
            <p className="text-muted-foreground">
              See how you rank against other student traders.
            </p>
          </div>

          {/* WebSocket Connection Status and Controls */}
          <div className="flex items-center gap-3">
            {useWebSocket && (
              <div className="flex items-center gap-2 text-sm">
                {isConnected ? (
                  <>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-green-600">Live</span>
                  </>
                ) : wsError ? (
                  <>
                    <div className="w-2 h-2 bg-red-500 rounded-full" />
                    <span className="text-red-600">Disconnected</span>
                  </>
                ) : (
                  <>
                    <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                    <span className="text-yellow-600">Connecting...</span>
                  </>
                )}
              </div>
            )}
            <Button
              onClick={useWebSocket ? reconnect : refreshLeaderboard}
              disabled={showLoading}
              variant="outline"
              size="sm"
            >
              {showLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {useWebSocket ? "Connecting..." : "Refreshing..."}
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  {useWebSocket ? "Reconnect" : "Refresh"}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {showLoading ? (
        <div className="flex justify-center items-center py-12">
          <div className="text-muted-foreground">
            {useWebSocket
              ? "Connecting to live updates..."
              : "Loading leaderboard..."}
          </div>
        </div>
      ) : displayLeaderboard.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-16 w-16 text-muted-foreground/50 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Rankings Yet</h3>
          <p className="text-muted-foreground">
            {wsError ? "Failed to connect to live updates. " : ""}
            Start trading to see rankings appear here!
          </p>
        </div>
      ) : (
        <>
          {/* Top 3 Highlight Cards */}
          {displayLeaderboard.length >= 3 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {displayLeaderboard.slice(0, 3).map((trader) => (
                <Card
                  key={trader.userId}
                  className={`hover:bg-accent/50 transition-colors ${
                    trader.rank === 1 ? "ring-2 ring-yellow-600" : ""
                  }`}
                >
                  <CardHeader className="text-center pb-2">
                    <div className="flex justify-center mb-2">
                      {trader.rank === 1 && (
                        <Trophy className="h-8 w-8 text-yellow-500" />
                      )}
                      {trader.rank === 2 && (
                        <Medal className="h-8 w-8 text-gray-400" />
                      )}
                      {trader.rank === 3 && (
                        <Award className="h-8 w-8 text-amber-600" />
                      )}
                    </div>
                    <CardTitle className="text-lg">{trader.userName}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <div className="flex justify-center mb-4">
                      <Avatar className="h-16 w-16">
                        <AvatarImage
                          src={trader.userAvatar || "/placeholder.svg"}
                          alt={trader.userName}
                        />
                        <AvatarFallback className="bg-primary text-primary-foreground text-lg">
                          {trader.userName.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </div>
                    <div className="space-y-2">
                      <p className="text-2xl font-bold">
                        ₹{(trader.portfolioValue ?? 0).toLocaleString()}
                      </p>
                      <Badge
                        className={`${
                          (trader.totalReturnPercent ?? 0) >= 0
                            ? "bg-green-600 hover:bg-green-700"
                            : "bg-red-600 hover:bg-red-700"
                        }`}
                      >
                        {(trader.totalReturnPercent ?? 0) >= 0 ? "+" : ""}
                        {(trader.totalReturnPercent ?? 0).toFixed(2)}%
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Full Leaderboard Table */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Full Rankings
              </CardTitle>
              <CardDescription>
                Complete leaderboard of all student traders
              </CardDescription>
            </CardHeader>
            <CardContent>
              {displayLeaderboard.length === 0 && !showLoading ? (
                <div className="text-center py-8">
                  <Trophy className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Traders Yet</h3>
                  <p className="text-muted-foreground">
                    Start trading to appear on the leaderboard!
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Rank</TableHead>
                      <TableHead>Trader</TableHead>
                      <TableHead>Portfolio Value</TableHead>
                      <TableHead>Total Return</TableHead>
                      <TableHead>Gain %</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {displayLeaderboard.map((trader) => (
                      <TableRow
                        key={trader.userId}
                        className={`hover:bg-accent/50 ${
                          trader.rank <= 3 ? "bg-accent/30" : ""
                        }`}
                      >
                        <TableCell className="font-medium">
                          {getRankBadge(trader.rank)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage
                                src={trader.userAvatar || "/placeholder.svg"}
                                alt={trader.userName}
                              />
                              <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                                {trader.userName.slice(0, 2).toUpperCase()}
                              </AvatarFallback>
                            </Avatar>
                            <span className="font-medium">
                              {trader.userName}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="font-semibold">
                          ₹{(trader.portfolioValue ?? 0).toLocaleString()}
                        </TableCell>
                        <TableCell
                          className={`font-semibold ${
                            (trader.totalReturn ?? 0) >= 0
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {(trader.totalReturn ?? 0) >= 0 ? "+" : ""}₹
                          {(trader.totalReturn ?? 0).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={`${
                              (trader.totalReturnPercent ?? 0) >= 0
                                ? "bg-green-600 hover:bg-green-700"
                                : "bg-red-600 hover:bg-red-700"
                            }`}
                          >
                            {(trader.totalReturnPercent ?? 0) >= 0 ? "+" : ""}
                            {(trader.totalReturnPercent ?? 0).toFixed(2)}%
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </MainLayout>
  );
}
