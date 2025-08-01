"use client";

import { AlertCircle, XCircle, AlertTriangle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

interface ErrorMessageProps {
  title?: string;
  message: string;
  severity?: "error" | "warning" | "info";
  onRetry?: () => void;
}

export function ErrorMessage({
  title,
  message,
  severity = "error",
  onRetry,
}: ErrorMessageProps) {
  const Icon =
    severity === "error"
      ? XCircle
      : severity === "warning"
      ? AlertTriangle
      : AlertCircle;

  const alertVariant =
    severity === "error"
      ? "destructive"
      : severity === "warning"
      ? "default"
      : "default";

  const defaultTitle =
    severity === "error"
      ? "Error"
      : severity === "warning"
      ? "Warning"
      : "Information";

  return (
    <Alert variant={alertVariant}>
      <Icon className="h-4 w-4" />
      <AlertTitle>{title || defaultTitle}</AlertTitle>
      <AlertDescription>
        <div className="flex flex-col gap-3">
          <p>{message}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="self-start"
            >
              Try Again
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}

interface ApiErrorFallbackProps {
  error: string | null;
  isLoading: boolean;
  onRetry?: () => void;
  children: React.ReactNode;
}

export function ApiErrorFallback({
  error,
  isLoading,
  onRetry,
  children,
}: ApiErrorFallbackProps) {
  if (error) {
    return <ErrorMessage message={error} onRetry={onRetry} />;
  }

  return children;
}
