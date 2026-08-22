import { Button } from "@/components/Button";
import { Icon } from "../icons";

export type PaginationProps = {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
};

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <nav aria-label="Paginação" className="flex items-center gap-2">
      <Button
        type="button"
        variant="secondary"
        size="icon"
        aria-label="Página anterior"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        <Icon name="previous" />
      </Button>
      <span className="min-w-24 text-center text-sm text-text-muted" aria-live="polite">
        Página {page} de {totalPages}
      </span>
      <Button
        type="button"
        variant="secondary"
        size="icon"
        aria-label="Próxima página"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        <Icon name="next" />
      </Button>
    </nav>
  );
}
