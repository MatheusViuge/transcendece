import { useEffect, useId, type ReactNode } from "react";
import { Icon } from "../icons";

export type ModalProps = {
  open: boolean;
  title: string;
  description?: string;
  children?: ReactNode;
  onClose: () => void;
};

export function Modal({ open, title, description, children, onClose }: ModalProps) {
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] grid place-items-center bg-black/40 p-4"
      onMouseDown={(event) => {
        if (event.currentTarget === event.target) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className="relative w-full max-w-lg rounded-card border border-border bg-surface p-6 shadow-dialog"
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 grid min-h-11 min-w-11 place-items-center rounded-control text-text-muted hover:bg-surface-muted hover:text-text"
          aria-label="Fechar modal"
        >
          <Icon name="close" />
        </button>
        <h2 id={titleId} className="pr-12 text-xl font-semibold text-text">{title}</h2>
        {description && <p id={descriptionId} className="mt-2 text-sm leading-6 text-text-muted">{description}</p>}
        {children && <div className="mt-5">{children}</div>}
      </section>
    </div>
  );
}
