"use client";

import { useState, useEffect, useMemo } from "react";
import { useTheme } from "next-themes";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Bar,
  ReferenceLine,
  Customized,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { stockService } from "@/services/api";

interface StockChartProps {
  symbol: string;
  currentPrice: number;
  change: number;
  changePercent: number;
}

interface ChartDataPoint {
  time: string;
  price: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  timestamp: number;
}

type TimeRange = "1D" | "1W" | "1M" | "3M" | "1Y";

// Helper function to sample data by time interval
const sampleDataByInterval = (
  data: ChartDataPoint[],
  intervalMs: number
): ChartDataPoint[] => {
  if (data.length === 0) return data;

  const sampledData: ChartDataPoint[] = [];
  let lastTimestamp = 0;

  for (const point of data) {
    if (
      sampledData.length === 0 ||
      point.timestamp - lastTimestamp >= intervalMs
    ) {
      sampledData.push(point);
      lastTimestamp = point.timestamp;
    }
  }

  return sampledData;
};

// Helper function to sample data per day
const sampleDataPerDay = (
  data: ChartDataPoint[],
  pointsPerDay: number
): ChartDataPoint[] => {
  if (data.length === 0) return data;

  // Group data by day
  const dataByDay: { [key: string]: ChartDataPoint[] } = {};

  data.forEach((point) => {
    const date = new Date(point.timestamp);
    const dayKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;

    if (!dataByDay[dayKey]) {
      dataByDay[dayKey] = [];
    }
    dataByDay[dayKey].push(point);
  });

  // Sample points from each day
  const sampledData: ChartDataPoint[] = [];

  Object.values(dataByDay).forEach((dayData) => {
    if (dayData.length <= pointsPerDay) {
      sampledData.push(...dayData);
    } else {
      // Sample evenly throughout the day
      const step = Math.floor(dayData.length / pointsPerDay);
      for (let i = 0; i < pointsPerDay; i++) {
        const index = Math.min(i * step, dayData.length - 1);
        sampledData.push(dayData[index]);
      }
    }
  });

  // Sort by timestamp
  return sampledData.sort((a, b) => a.timestamp - b.timestamp);
};

// Custom Candlestick component
const Candlestick = ({ payload, x, y, width, height }: any) => {
  if (
    !payload ||
    !payload.open ||
    !payload.close ||
    !payload.high ||
    !payload.low
  ) {
    return null;
  }

  const { open, close, high, low } = payload;
  const isRising = close > open;
  const color = isRising ? "#00ff88" : "#ff4757";
  const bodyHeight =
    Math.abs(close - open) * (height / (payload.yMax - payload.yMin));
  const bodyY =
    y +
    (payload.yMax - Math.max(open, close)) *
      (height / (payload.yMax - payload.yMin));

  const wickTop =
    y + (payload.yMax - high) * (height / (payload.yMax - payload.yMin));
  const wickBottom =
    y + (payload.yMax - low) * (height / (payload.yMax - payload.yMin));

  const candleWidth = Math.max(width * 0.6, 1);
  const wickX = x + width / 2;
  const bodyX = x + (width - candleWidth) / 2;

  return (
    <g>
      {/* Wick lines */}
      <line
        x1={wickX}
        y1={wickTop}
        x2={wickX}
        y2={wickBottom}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body rectangle */}
      <rect
        x={bodyX}
        y={bodyY}
        width={candleWidth}
        height={Math.max(bodyHeight, 1)}
        fill={isRising ? "transparent" : color}
        stroke={color}
        strokeWidth={1}
      />
    </g>
  );
};

// Professional Trading Tooltip
const TradingTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const isRising = data.close > data.open;

  return (
    <div className="bg-popover border border-border rounded-lg p-3 shadow-lg text-xs">
      <div className="text-popover-foreground mb-2 font-mono">{label}</div>
      {data.open && (
        <div className="space-y-1 font-mono">
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">O:</span>
            <span className="text-popover-foreground">
              ₹{data.open.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">H:</span>
            <span className="text-green-400">₹{data.high.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">L:</span>
            <span className="text-red-400">₹{data.low.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-muted-foreground">C:</span>
            <span className={isRising ? "text-green-400" : "text-red-400"}>
              ₹{data.close.toFixed(2)}
            </span>
          </div>
          {data.volume && (
            <div className="flex justify-between gap-4 border-t border-border pt-1 mt-1">
              <span className="text-muted-foreground">Vol:</span>
              <span className="text-primary">
                {(data.volume / 1000).toFixed(1)}K
              </span>
            </div>
          )}
        </div>
      )}
      {!data.open && (
        <div className="font-mono">
          <span className="text-muted-foreground">Price: </span>
          <span className="text-popover-foreground">
            ₹{data.price.toFixed(2)}
          </span>
        </div>
      )}
    </div>
  );
};

export function StockChart({
  symbol,
  currentPrice,
  change,
  changePercent,
}: StockChartProps) {
  const { theme } = useTheme();
  const [selectedRange, setSelectedRange] = useState<TimeRange>("1D");
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showVolume, setShowVolume] = useState(true);

  const [dataCache, setDataCache] = useState<Record<string, ChartDataPoint[]>>(
    {}
  );

  const isPositive = change >= 0;
  const timeRanges: TimeRange[] = ["1D", "1W", "1M", "3M", "1Y"];

  // Enhanced data loading
  useEffect(() => {
    const abortController = new AbortController();
    let timeoutId: NodeJS.Timeout;

    const loadChartData = async () => {
      if (!symbol || !currentPrice) return;

      timeoutId = setTimeout(async () => {
        if (abortController.signal.aborted) return;

        const cacheKey = `${symbol}-${selectedRange}`;
        if (dataCache[cacheKey]) {
          const cachedData = [...dataCache[cacheKey]];
          if (cachedData.length > 0) {
            cachedData[cachedData.length - 1].price = currentPrice;
            if (cachedData[cachedData.length - 1].close) {
              cachedData[cachedData.length - 1].close = currentPrice;
            }
          }
          setChartData(cachedData);
          setError(null);
          return;
        }

        setIsLoading(true);
        setError(null);

        try {
          const periodMap: Record<TimeRange, string> = {
            "1D": "1d",
            "1W": "5d",
            "1M": "1mo",
            "3M": "3mo",
            "1Y": "1y",
          };

          // Map to appropriate intervals for data granularity
          const intervalMap: Record<TimeRange, string> = {
            "1D": "30m", // 30-minute intervals for 1 day
            "1W": "1h", // 1-hour intervals for 1 week (will be filtered to 4 per day)
            "1M": "1d", // Daily intervals for 1 month
            "3M": "1d", // Daily intervals for 3 months
            "1Y": "1d", // Daily intervals for 1 year
          };

          const period = periodMap[selectedRange];
          const interval = intervalMap[selectedRange];

          if (abortController.signal.aborted) return;

          // Request data from API with specific interval
          const apiData = await stockService.getStockPriceHistory(
            symbol,
            period,
            interval
          );

          if (abortController.signal.aborted) return;

          const dataArray = apiData?.data || apiData || [];

          if (dataArray && Array.isArray(dataArray) && dataArray.length > 0) {
            let processedData: ChartDataPoint[] = dataArray.map(
              (point: any, index: number) => {
                const price =
                  point.close || point.price || point.adjClose || currentPrice;

                let timestamp;
                if (point.date) {
                  timestamp = new Date(point.date).getTime();
                } else {
                  timestamp =
                    point.timestamp ||
                    Date.now() - (dataArray.length - index) * 60000;
                }

                // Try to extract OHLCV data if available
                const open = point.open || price;
                const high = point.high || price * 1.02;
                const low = point.low || price * 0.98;
                const close = price;
                const volume = point.volume || Math.random() * 100000;

                return {
                  time: formatTimeLabel(timestamp, selectedRange, index),
                  price: parseFloat(close) || currentPrice,
                  open: parseFloat(open),
                  high: parseFloat(high),
                  low: parseFloat(low),
                  close: parseFloat(close),
                  volume: parseInt(volume),
                  timestamp: new Date(timestamp).getTime(),
                };
              }
            );

            // Filter data based on requirements
            if (selectedRange === "1D") {
              // For 1D: Show 30-minute intervals
              const targetIntervalMs = 30 * 60 * 1000; // 30 minutes
              processedData = sampleDataByInterval(
                processedData,
                targetIntervalMs
              );
            } else if (selectedRange === "1W") {
              // For 1W: Show 4 data points per day
              processedData = sampleDataPerDay(processedData, 4);
            }

            if (processedData.length > 0) {
              processedData[processedData.length - 1].price = currentPrice;
              processedData[processedData.length - 1].close = currentPrice;
            }

            if (!abortController.signal.aborted) {
              setChartData(processedData);
              setDataCache((prev) => ({
                ...prev,
                [cacheKey]: processedData,
              }));
            }
          } else {
            // No data available from API
            if (!abortController.signal.aborted) {
              setError("No historical data available");
              setChartData([]);
            }
          }
        } catch (error) {
          if (!abortController.signal.aborted) {
            console.error("API Error:", error);
            setError("No historical data available");
            setChartData([]);
          }
        } finally {
          if (!abortController.signal.aborted) {
            setIsLoading(false);
          }
        }
      }, 500);
    };

    loadChartData();

    return () => {
      clearTimeout(timeoutId);
      abortController.abort();
    };
  }, [selectedRange, symbol]);

  // Update current price in existing data
  useEffect(() => {
    if (chartData.length > 0 && currentPrice) {
      setChartData((prevData) => {
        const updatedData = [...prevData];
        if (updatedData.length > 0) {
          updatedData[updatedData.length - 1] = {
            ...updatedData[updatedData.length - 1],
            price: currentPrice,
            close: currentPrice,
          };
        }
        return updatedData;
      });
    }
  }, [currentPrice]);

  const formatTimeLabel = (
    timestamp: string | number,
    range: TimeRange,
    index: number
  ): string => {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) return `Point ${index + 1}`;

      switch (range) {
        case "1D":
          return date.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
          });
        case "1W":
          return date.toLocaleDateString("en-US", { weekday: "short" });
        case "1M":
          return date.toLocaleDateString("en-US", { day: "numeric" });
        case "3M":
          return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          });
        case "1Y":
          return date.toLocaleDateString("en-US", { month: "short" });
        default:
          return date.toLocaleDateString();
      }
    } catch (error) {
      return `Point ${index + 1}`;
    }
  };

  // Calculate price levels for reference lines and timeframe-specific changes
  const priceStats = useMemo(() => {
    if (chartData.length === 0) return null;

    const prices = chartData.map((d) => d.price);
    const highs = chartData.map((d) => d.high || d.price);
    const lows = chartData.map((d) => d.low || d.price);

    // Calculate change based on timeframe
    const firstPrice = chartData[0]?.price || currentPrice;
    const lastPrice = chartData[chartData.length - 1]?.price || currentPrice;
    const timeframeChange = lastPrice - firstPrice;
    const timeframeChangePercent =
      firstPrice > 0 ? (timeframeChange / firstPrice) * 100 : 0;

    return {
      dayHigh: Math.max(...highs),
      dayLow: Math.min(...lows),
      avgPrice: prices.reduce((a, b) => a + b, 0) / prices.length,
      timeframeChange,
      timeframeChangePercent,
      isTimeframePositive: timeframeChange >= 0,
    };
  }, [chartData, currentPrice]);

  return (
    <Card className="bg-card border-border text-card-foreground">
      <CardHeader className="border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-card-foreground">
              <Activity className="h-5 w-5" />
              {symbol}
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Professional Trading Chart {error && `(${error})`}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {priceStats ? (
              <>
                {priceStats.isTimeframePositive ? (
                  <TrendingUp className="h-4 w-4 text-green-400" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-400" />
                )}
                <span
                  className={`text-sm font-mono ${
                    priceStats.isTimeframePositive
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {priceStats.isTimeframePositive ? "+" : ""}₹
                  {priceStats.timeframeChange.toFixed(2)} (
                  {priceStats.timeframeChangePercent.toFixed(2)}%)
                </span>
                <span className="text-xs text-gray-500 ml-2">
                  {selectedRange}
                </span>
              </>
            ) : (
              <>
                {isPositive ? (
                  <TrendingUp className="h-4 w-4 text-green-400" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-400" />
                )}
                <span
                  className={`text-sm font-mono ${
                    isPositive ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isPositive ? "+" : ""}₹{change.toFixed(2)} (
                  {changePercent.toFixed(2)}%)
                </span>
              </>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0 bg-card">
        {/* Controls */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex gap-1">
            {timeRanges.map((range) => (
              <Button
                key={range}
                variant={selectedRange === range ? "default" : "ghost"}
                size="sm"
                onClick={() => setSelectedRange(range)}
                className={`text-xs h-7 ${
                  selectedRange === range
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
              >
                {range}
              </Button>
            ))}
          </div>

          <div className="flex gap-1">
            {chartData.some((d) => d.volume) && (
              <Button
                variant={showVolume ? "default" : "ghost"}
                size="sm"
                onClick={() => setShowVolume(!showVolume)}
                className={`text-xs h-7 ${
                  showVolume
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                }`}
              >
                Volume
              </Button>
            )}
          </div>
        </div>

        {/* Chart */}
        <div
          className="w-full bg-card"
          style={{
            height: showVolume ? "500px" : "400px",
            backgroundColor: theme === "dark" ? "#030712" : undefined,
          }}
        >
          {isLoading ? (
            <div
              className="flex items-center justify-center h-full bg-card"
              style={{
                backgroundColor: theme === "dark" ? "#030712" : undefined,
              }}
            >
              <div className="text-muted-foreground">
                Loading professional chart...
              </div>
            </div>
          ) : chartData.length === 0 ? (
            <div
              className="flex items-center justify-center h-full bg-card"
              style={{
                backgroundColor: theme === "dark" ? "#030712" : undefined,
              }}
            >
              <div className="text-muted-foreground">
                No chart data available
              </div>
            </div>
          ) : (
            <div
              className="w-full h-full bg-card"
              style={{
                backgroundColor: theme === "dark" ? "#030712" : undefined,
              }}
            >
              <ResponsiveContainer
                width="100%"
                height="100%"
                className="bg-card"
                style={{
                  backgroundColor: theme === "dark" ? "#030712" : undefined,
                }}
              >
                <ComposedChart
                  data={chartData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  {/* Force theme-aware background on the SVG surface */}
                  <Customized
                    component={(props: any) => (
                      <rect
                        width={props.width}
                        height={props.height}
                        fill={theme === "dark" ? "#030712" : "#ffffff"}
                      />
                    )}
                  />

                  <defs>
                    <linearGradient
                      id="priceGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="5%"
                        stopColor={
                          priceStats?.isTimeframePositive
                            ? "#00ff88"
                            : "#ff4757"
                        }
                        stopOpacity={0.3}
                      />
                      <stop
                        offset="95%"
                        stopColor={
                          priceStats?.isTimeframePositive
                            ? "#00ff88"
                            : "#ff4757"
                        }
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  {/* Professional grid */}
                  <CartesianGrid
                    strokeDasharray="1 1"
                    stroke="#333"
                    horizontal={true}
                    vertical={false}
                  />

                  <XAxis
                    dataKey="time"
                    axisLine={false}
                    tickLine={false}
                    className="text-xs"
                    tick={{ fill: "#666", fontSize: 10 }}
                    interval="preserveStartEnd"
                  />

                  <YAxis
                    yAxisId="price"
                    orientation="right"
                    axisLine={false}
                    tickLine={false}
                    className="text-xs"
                    tick={{ fill: "#666", fontSize: 10 }}
                    tickFormatter={(value) => `₹${value.toFixed(0)}`}
                    domain={["dataMin - 1", "dataMax + 1"]}
                    width={60}
                  />

                  {showVolume && chartData.some((d) => d.volume) && (
                    <YAxis
                      yAxisId="volume"
                      orientation="left"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: "#666", fontSize: 10 }}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                      domain={[0, "dataMax * 4"]}
                      width={50}
                    />
                  )}

                  <Tooltip content={<TradingTooltip />} />

                  {/* Reference lines */}
                  {priceStats && (
                    <>
                      <ReferenceLine
                        yAxisId="price"
                        y={priceStats.dayHigh}
                        stroke="#ff6b6b"
                        strokeDasharray="2 2"
                        strokeOpacity={0.5}
                      />
                      <ReferenceLine
                        yAxisId="price"
                        y={priceStats.dayLow}
                        stroke="#4ecdc4"
                        strokeDasharray="2 2"
                        strokeOpacity={0.5}
                      />
                    </>
                  )}

                  {/* Volume bars */}
                  {showVolume && chartData.some((d) => d.volume) && (
                    <Bar
                      yAxisId="volume"
                      dataKey="volume"
                      fill="#444"
                      fillOpacity={0.3}
                      stroke="none"
                    />
                  )}

                  {/* Price line */}
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="price"
                    stroke={
                      priceStats?.isTimeframePositive ? "#00ff88" : "#ff4757"
                    }
                    strokeWidth={1.5}
                    dot={false}
                    activeDot={{
                      r: 3,
                      fill: priceStats?.isTimeframePositive
                        ? "#00ff88"
                        : "#ff4757",
                    }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Professional footer */}
        <div className="p-4 border-t border-border bg-muted/50">
          <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
            <div className="flex gap-6">
              <span>Points: {chartData.length}</span>
              <span>Range: {selectedRange}</span>
              {priceStats && (
                <>
                  <span className="text-red-400">
                    H: ₹{priceStats.dayHigh.toFixed(2)}
                  </span>
                  <span className="text-green-400">
                    L: ₹{priceStats.dayLow.toFixed(2)}
                  </span>
                  <span
                    className={`${
                      priceStats.isTimeframePositive
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {selectedRange} Change:{" "}
                    {priceStats.isTimeframePositive ? "+" : ""}₹
                    {priceStats.timeframeChange.toFixed(2)}
                  </span>
                </>
              )}
            </div>
            <div className="text-lg font-bold text-foreground">
              ₹{currentPrice.toFixed(2)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
