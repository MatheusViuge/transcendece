import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const spinnerStyles = tv({
  base: "inline-block animate-spin rounded-full border-2 border-current border-r-transparent",
  variants: {
    size: {
      sm: "h-4 w-4",
      md: "h-5 w-5",
      lg: "h-8 w-8",
    },
  },
  defaultVariants: { size: "md" },
});

type SpinnerProps = ComponentProps<"span"> &
  VariantProps<typeof spinnerStyles> & {
    label?: string;
  };

export function Spinner({ size, label = "Carregando", className, ...props }: SpinnerProps) {
  return (
    <span role="status" aria-label={label} className={spinnerStyles({ size, className })} {...props} />
  );
}
