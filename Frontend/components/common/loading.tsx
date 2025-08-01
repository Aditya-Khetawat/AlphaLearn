"use client";

import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  centered?: boolean;
}

export function LoadingSpinner({
  size = "md",
  text = "Loading...",
  centered = false,
}: LoadingSpinnerProps) {
  const sizeClass =
    size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-6 w-6";

  const containerClass = centered
    ? "flex flex-col items-center justify-center w-full py-8"
    : "flex items-center gap-2";

  return (
    <div className={containerClass}>
      <Loader2 className={`${sizeClass} animate-spin`} />
      {text && <p className="text-muted-foreground">{text}</p>}
    </div>
  );
}

interface LoadingSkeletonProps {
  rows?: number;
  height?: string;
  className?: string;
}

export function LoadingSkeleton({
  rows = 3,
  height = "h-12",
  className = "",
}: LoadingSkeletonProps) {
  return (
    <div className="w-full space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className={`rounded-md bg-muted animate-pulse ${height} ${className}`}
        />
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="w-full space-y-3">
      {/* Header */}
      <div className="flex w-full space-x-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={`header-${i}`}
            className="h-8 flex-1 rounded-md bg-muted animate-pulse"
          />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={`row-${i}`} className="flex w-full space-x-2">
          {Array.from({ length: 4 }).map((_, j) => (
            <div
              key={`cell-${i}-${j}`}
              className="h-10 flex-1 rounded-md bg-muted animate-pulse"
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="h-6 w-1/3 rounded-md bg-muted animate-pulse" />
      <div className="h-4 w-1/2 rounded-md bg-muted animate-pulse" />
      <div className="h-20 w-full rounded-md bg-muted animate-pulse" />
    </div>
  );
}
