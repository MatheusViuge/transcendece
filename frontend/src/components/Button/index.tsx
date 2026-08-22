import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const buttonStyles = tv({
  base: "inline-flex items-center justify-center gap-2 rounded-control border border-solid font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 hover:cursor-pointer",
  variants: {
    variant: {
      primary: "border-transparent bg-text text-white hover:bg-gray",
      secondary: "border-border-strong bg-surface text-text hover:border-border hover:bg-surface-muted",
      accent: "border-transparent bg-primary text-white hover:bg-primary-hover",
      danger: "border-transparent bg-danger text-white hover:brightness-90",
      ghost: "border-transparent bg-transparent text-text hover:bg-surface-muted",
      badge: "min-h-6 border-transparent bg-text px-2 py-1 text-xs text-white hover:bg-gray",
    },
    size: {
      sm: "min-h-9 px-3 text-sm",
      md: "min-h-11 px-4 text-sm",
      lg: "min-h-12 px-5 text-base",
      icon: "min-h-11 min-w-11 p-2",
    },
    fullWidth: {
      true: "w-full",
      false: "w-auto",
    },
  },
  defaultVariants: {
    variant: "primary",
    size: "md",
    fullWidth: false,
  },
});

type ButtonSchema = VariantProps<typeof buttonStyles>;
interface ButtonProps extends ComponentProps<"button">, ButtonSchema {
  loading?: boolean;
}

export function Button({
  className,
  variant,
  size,
  fullWidth,
  loading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={buttonStyles({ variant, size, fullWidth, className })}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading && (
        <span
          aria-hidden="true"
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-r-transparent"
        />
      )}
      {children}
    </button>
  );
}
