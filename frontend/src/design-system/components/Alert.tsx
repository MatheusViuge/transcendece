import type { ComponentProps, ReactNode } from "react";
import { tv, type VariantProps } from "tailwind-variants";
import { Icon, type SystemIconName } from "../icons";

const alertStyles = tv({
  slots: {
    root: "flex items-start gap-3 rounded-card border p-4 text-sm",
    content: "min-w-0 flex-1",
    title: "mb-1 font-semibold",
  },
  variants: {
    tone: {
      info: { root: "border-primary-border bg-info-soft text-text", title: "text-primary" },
      success: { root: "border-success/20 bg-success-soft text-text", title: "text-success" },
      warning: { root: "border-warning/20 bg-warning-soft text-text", title: "text-warning" },
      danger: { root: "border-danger/20 bg-danger-soft text-text", title: "text-danger" },
    },
  },
  defaultVariants: { tone: "info" },
});

type AlertTone = "info" | "success" | "warning" | "danger";

const toneIcons: Record<AlertTone, SystemIconName> = {
  info: "info",
  success: "success",
  warning: "warning",
  danger: "danger",
};

type AlertProps = Omit<ComponentProps<"div">, "title"> &
  VariantProps<typeof alertStyles> & {
    title?: ReactNode;
  };

export function Alert({ tone, title, children, className, ...props }: AlertProps) {
  const resolvedTone: AlertTone = tone ?? "info";
  const { root, content, title: titleStyle } = alertStyles({ tone: resolvedTone });

  return (
    <div
      role={resolvedTone === "danger" ? "alert" : "status"}
      className={root({ className })}
      {...props}
    >
      <Icon name={toneIcons[resolvedTone]} className="mt-0.5 shrink-0" />
      <div className={content()}>
        {title && <div className={titleStyle()}>{title}</div>}
        <div>{children}</div>
      </div>
    </div>
  );
}
