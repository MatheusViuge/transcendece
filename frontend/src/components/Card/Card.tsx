import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const cardStyles = tv({
  base: "overflow-hidden rounded-card border border-border bg-surface transition-shadow",
  variants: {
    interactive: {
      true: "cursor-pointer hover:shadow-card",
      false: "cursor-default",
    },
    elevated: {
      true: "shadow-card",
      false: "shadow-none",
    },
  },
  defaultVariants: {
    interactive: true,
    elevated: false,
  },
});

type CardSchema = VariantProps<typeof cardStyles>;
interface CardProps extends ComponentProps<"div">, CardSchema {}

export function Card({ className, children, interactive, elevated, ...props }: CardProps) {
  return (
    <div className={cardStyles({ interactive, elevated, className })} {...props}>
      {children}
    </div>
  );
}
