import type { ComponentProps } from "react";
import { tv, type VariantProps } from "tailwind-variants";

const badgeStyles = tv({
  base: "inline-flex min-h-6 items-center rounded-pill border px-2.5 py-0.5 text-xs font-semibold leading-5",
  variants: {
    tone: {
      neutral: "border-border bg-surface-muted text-text-muted",
      primary: "border-primary-border bg-primary-soft text-primary",
      success: "border-success/20 bg-success-soft text-success",
      warning: "border-warning/20 bg-warning-soft text-warning",
      danger: "border-danger/20 bg-danger-soft text-danger",
    },
  },
  defaultVariants: {
    tone: "neutral",
  },
});

type BadgeSchema = VariantProps<typeof badgeStyles>;
type BadgeProps = ComponentProps<"span"> & BadgeSchema;

export function Badge({ tone, className, ...props }: BadgeProps) {
  return <span className={badgeStyles({ tone, className })} {...props} />;
}
