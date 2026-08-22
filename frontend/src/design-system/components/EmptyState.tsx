import type { ReactNode } from "react";
import { Icon } from "../icons";
import type { SystemIconName } from "../iconRegistry";

export type EmptyStateProps = {
  title: string;
  description?: string;
  icon?: SystemIconName;
  action?: ReactNode;
  className?: string;
};

export function EmptyState({
  title,
  description,
  icon = "info",
  action,
  className = "",
}: EmptyStateProps) {
  return (
    <section className={`mx-auto flex w-full max-w-md flex-col items-center gap-4 text-center ${className}`}>
      <div className="grid h-16 w-16 place-items-center rounded-full bg-primary-soft text-primary">
        <Icon name={icon} size="xl" />
      </div>
      <div>
        <h2 className="text-xl font-semibold text-text">{title}</h2>
        {description && <p className="mt-2 text-sm leading-6 text-text-muted">{description}</p>}
      </div>
      {action && <div className="mt-1 w-full">{action}</div>}
    </section>
  );
}
