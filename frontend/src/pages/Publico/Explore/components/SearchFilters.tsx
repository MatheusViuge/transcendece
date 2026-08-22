import { Button } from "@/components/Button";
import type { ICourseSearchData } from "@/interfaces/cursos";
import type { SearchOrder, SearchPrice, SearchSort, SearchState } from "../searchState";

const selectClassName =
  "min-h-11 w-full rounded-control border border-border bg-surface px-3 text-sm text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary";

type SearchFiltersProps = {
  state: SearchState;
  facets: ICourseSearchData["facets"];
  onChange: (patch: Partial<SearchState>) => void;
  onClear: () => void;
};

export function SearchFilters({ state, facets, onChange, onClear }: SearchFiltersProps) {
  return (
    <aside className="grid content-start gap-5 rounded-card border border-border bg-surface p-5" aria-label="Filtros de cursos">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold text-text">Filtros</h2>
        <Button type="button" variant="ghost" size="sm" onClick={onClear}>
          Limpar
        </Button>
      </div>

      <label className="grid gap-2 text-sm font-medium text-text">
        Categoria
        <select
          className={selectClassName}
          value={state.categoryId ?? ""}
          onChange={(event) => onChange({ categoryId: event.target.value ? Number(event.target.value) : null, page: 1 })}
        >
          <option value="">Todas</option>
          {facets.categories.map((option) => (
            <option key={option.id} value={option.id}>{option.label}</option>
          ))}
        </select>
      </label>

      <label className="grid gap-2 text-sm font-medium text-text">
        Nível
        <select
          className={selectClassName}
          value={state.levelId ?? ""}
          onChange={(event) => onChange({ levelId: event.target.value ? Number(event.target.value) : null, page: 1 })}
        >
          <option value="">Todos</option>
          {facets.levels.map((option) => (
            <option key={option.id} value={option.id}>{option.label}</option>
          ))}
        </select>
      </label>

      <label className="grid gap-2 text-sm font-medium text-text">
        Instrutor
        <select
          className={selectClassName}
          value={state.instructorId ?? ""}
          onChange={(event) => onChange({ instructorId: event.target.value ? Number(event.target.value) : null, page: 1 })}
        >
          <option value="">Todos</option>
          {facets.instructors.map((option) => (
            <option key={option.id} value={option.id}>{option.label}</option>
          ))}
        </select>
      </label>

      <label className="grid gap-2 text-sm font-medium text-text">
        Preço
        <select
          className={selectClassName}
          value={state.price ?? ""}
          onChange={(event) => onChange({ price: (event.target.value || null) as SearchPrice | null, page: 1 })}
        >
          <option value="">Todos</option>
          <option value="free">Gratuitos</option>
          <option value="paid">Pagos</option>
        </select>
      </label>

      <label className="grid gap-2 text-sm font-medium text-text">
        Ordenar por
        <select
          className={selectClassName}
          value={state.sort}
          onChange={(event) => onChange({ sort: event.target.value as SearchSort, page: 1 })}
        >
          <option value="newest">Mais recentes</option>
          <option value="title">Título</option>
          <option value="price">Preço</option>
          <option value="rating">Avaliação</option>
        </select>
      </label>

      <label className="grid gap-2 text-sm font-medium text-text">
        Direção
        <select
          className={selectClassName}
          value={state.order}
          onChange={(event) => onChange({ order: event.target.value as SearchOrder, page: 1 })}
        >
          <option value="desc">Decrescente</option>
          <option value="asc">Crescente</option>
        </select>
      </label>
    </aside>
  );
}
