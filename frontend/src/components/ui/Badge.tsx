import * as React from "react"
import { cn } from "../../lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'error' | 'ai'
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-primary text-text-inverse hover:bg-primary-hover",
    secondary: "border-transparent bg-surface-muted text-text-secondary",
    outline: "text-text-primary border-border",
    success: "border-transparent bg-success-subtle text-success",
    warning: "border-transparent bg-warning-subtle text-warning",
    error: "border-transparent bg-error-subtle text-error",
    ai: "border-transparent bg-ai-light text-ai",
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
