"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface SimpleSwitchProps {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
}

export const SimpleSwitch = React.forwardRef<
  HTMLButtonElement,
  SimpleSwitchProps
>(({ checked = false, onCheckedChange, disabled = false, className }, ref) => {
  // Track internal state, but defer to external state if provided
  const [internalChecked, setInternalChecked] = React.useState(checked);

  // Update internal state when external state changes
  React.useEffect(() => {
    setInternalChecked(checked);
  }, [checked]);

  const handleClick = React.useCallback(() => {
    if (disabled) return;

    const newValue = !internalChecked;
    setInternalChecked(newValue);

    // Only call the callback if provided
    if (onCheckedChange) {
      onCheckedChange(newValue);
    }
  }, [disabled, internalChecked, onCheckedChange]);

  return (
    <button
      type="button"
      role="switch"
      aria-checked={internalChecked}
      data-state={internalChecked ? "checked" : "unchecked"}
      disabled={disabled}
      className={cn(
        "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50",
        internalChecked ? "bg-primary" : "bg-input",
        className
      )}
      onClick={handleClick}
      ref={ref}
    >
      <span
        className={cn(
          "pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform",
          internalChecked ? "translate-x-5" : "translate-x-0"
        )}
      />
    </button>
  );
});

SimpleSwitch.displayName = "SimpleSwitch";
