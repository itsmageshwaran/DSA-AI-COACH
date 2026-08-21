import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, type Theme } from '../../features/theme/ThemeContext';
import { cn } from '../../lib/utils';

interface ThemeToggleProps {
  className?: string;
  size?: 'sm' | 'md';
  variant?: 'segmented' | 'icon-button';
}

export function ThemeToggle({ className, size = 'sm', variant = 'segmented' }: ThemeToggleProps) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();

  const options: { value: Theme; label: string; icon: typeof Sun }[] = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'system', label: 'System', icon: Monitor },
    { value: 'dark', label: 'Dark', icon: Moon },
  ];

  if (variant === 'icon-button') {
    return (
      <button
        onClick={toggleTheme}
        className={cn(
          "relative p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-all focus-ring",
          className
        )}
        title={`Current theme: ${theme} (${resolvedTheme}). Click to toggle.`}
        aria-label={`Toggle theme, current: ${theme}`}
      >
        {resolvedTheme === 'dark' ? (
          <Moon className="w-4 h-4 text-accent transition-transform duration-200 hover:rotate-12" />
        ) : (
          <Sun className="w-4 h-4 text-warning transition-transform duration-200 hover:rotate-45" />
        )}
      </button>
    );
  }

  return (
    <div
      role="group"
      aria-label="Theme selection"
      className={cn(
        "inline-flex items-center p-0.5 rounded-lg bg-surface-muted border border-border/80 shadow-2xs",
        className
      )}
    >
      {options.map((opt) => {
        const Icon = opt.icon;
        const isActive = theme === opt.value;
        return (
          <button
            key={opt.value}
            onClick={() => setTheme(opt.value)}
            className={cn(
              "flex items-center justify-center rounded-md transition-all duration-150 relative focus-ring",
              size === 'sm' ? "h-7 w-7 text-xs" : "h-8 px-2.5 gap-1.5 text-xs font-medium",
              isActive
                ? "bg-surface text-text-primary shadow-xs font-semibold border border-border/40"
                : "text-text-muted hover:text-text-primary hover:bg-surface-hover/50"
            )}
            title={`Switch to ${opt.label} theme`}
            aria-label={`${opt.label} theme`}
            aria-pressed={isActive}
          >
            <Icon
              className={cn(
                "w-3.5 h-3.5 shrink-0 transition-colors",
                isActive && opt.value === 'light' && "text-amber-500 dark:text-amber-400",
                isActive && opt.value === 'dark' && "text-blue-500 dark:text-blue-400",
                isActive && opt.value === 'system' && "text-accent"
              )}
            />
            {size === 'md' && <span>{opt.label}</span>}
          </button>
        );
      })}
    </div>
  );
}
