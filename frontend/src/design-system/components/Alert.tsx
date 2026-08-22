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

const toneIcons: Record<NonNullable<VariantProps<typeof alertStyles>["tone"]>, SystemIconName> = {
  info: "info",
  success: "success",
  warning: "warning",
  danger: "danger",
};

type AlertProps = Omit<ComponentProps<"div">, "title"> &
  VariantProps<typeof alertStyles> & {
    title?: ReactNode;
  };

export function Alert({ tone = "info", title, children, className, ...props }: AlertProps) {
  const { root, content, title: titleStyle } = alertStyles({ tone });

  return (
    <div
      role={tone === "danger" ? "alert" : "status"}
      className={root({ className })}
      {...props}
    >
      <Icon name={toneIcons[tone]} className="mt-0.5 shrink-0" />
      <div className={content()}>
        {title && <div className={titleStyle()}>{title}</div>}
        <div>{children}</div>
      </div>
    </div>
  );
}
