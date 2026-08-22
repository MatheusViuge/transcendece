import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";

import { Button } from "@/components/Button";
import { BaseInput } from "@/components/Form";
import { Alert, Pagination, Spinner } from "@/design-system";
import type { ICourseSearchData } from "@/interfaces/cursos";
import { searchSchema } from "@/pages/Publico/schemas/searchSchema";
import { api, catchCustom } from "@/services/api";

import CoursesCount from "./components/CoursesCount";
import CoursesGrid from "./components/CoursesGrid";
import EmptyState from "./components/EmptyState";
import { SearchFilters } from "./components/SearchFilters";
import {
  buildSearchRequestParams,
  readSearchState,
  searchStateToParams,
  type SearchState,
} from "./searchState";

const EMPTY_FACETS: ICourseSearchData["facets"] = {
  categories: [],
  levels: [],
  instructors: [],
};

type SearchBoxProps = {
  initialQuery: string;
  onSearch: (query: string) => void;
};

function SearchBox({ initialQuery, onSearch }: SearchBoxProps) {
  const [queryInput, setQueryInput] = useState(initialQuery);
  const [queryError, setQueryError] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = searchSchema.safeParse({ busca: queryInput });

    if (!parsed.success) {
      setQueryError(parsed.error.issues[0]?.message ?? "Busca inválida.");
      return;
    }

    setQueryError(null);
    onSearch(parsed.data.busca);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="col-span-full grid gap-2 lg:grid-cols-[minmax(0,42rem)_auto] lg:items-start"
    >
      <div className="grid gap-1">
        <label htmlFor="buscar" className="text-sm font-medium text-text">
          Buscar cursos
        </label>
        <BaseInput
          id="buscar"
          value={queryInput}
          onChange={(event) => setQueryInput(event.target.value)}
          placeholder="Título, descrição, categoria, nível ou instrutor..."
          maxLength={120}
          aria-invalid={Boolean(queryError)}
        />
        {queryError && (
          <p className="text-xs text-danger" role="alert">
            {queryError}
          </p>
        )}
      </div>
      <Button type="submit" variant="accent" className="lg:mt-6">
        Buscar
      </Button>
    </form>
  );
}

type SearchResultsProps = {
  state: SearchState;
  onPageChange: (page: number) => void;
  onPageCorrection: (page: number) => void;
  onFacetsReady: (facets: ICourseSearchData["facets"]) => void;
};

function SearchResults({
  state,
  onPageChange,
  onPageCorrection,
  onFacetsReady,
}: SearchResultsProps) {
  const [result, setResult] = useState<ICourseSearchData | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    api.get<ICourseSearchData>({
      url: "/search/courses",
      config: { params: buildSearchRequestParams(state) },
      hiddenToast: true,
    })
      .then((response) => {
        if (!active) return;

        const maxPage = Math.max(response.data.pagination.total_pages, 1);
        if (state.page > maxPage) {
          onPageCorrection(maxPage);
          return;
        }

        setResult(response.data);
        onFacetsReady(response.data.facets);
      })
      .catch((error) => {
        if (!active) return;
        setRequestError("Não foi possível carregar os cursos. Tente novamente.");
        catchCustom(error);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [onFacetsReady, onPageCorrection, state]);

  if (loading) {
    return (
      <section className="grid min-h-64 place-items-center" aria-busy="true">
        <Spinner size="lg" label="Buscando cursos" />
      </section>
    );
  }

  if (requestError) {
    return (
      <section className="min-w-0">
        <Alert tone="danger" title="Erro na busca">
          {requestError}
        </Alert>
      </section>
    );
  }

  if (!result || result.items.length === 0) {
    return (
      <section className="min-w-0">
        <EmptyState />
      </section>
    );
  }

  return (
    <section className="grid min-w-0 gap-6">
      <CoursesCount count={result.pagination.total} />
      <CoursesGrid courses={result.items} />
      <Pagination
        page={result.pagination.page}
        totalPages={result.pagination.total_pages}
        onPageChange={onPageChange}
      />
    </section>
  );
}

export default function Explore() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchKey = searchParams.toString();
  const state = useMemo(
    () => readSearchState(new URLSearchParams(searchKey)),
    [searchKey],
  );
  const canonicalKey = useMemo(
    () => searchStateToParams(state).toString(),
    [state],
  );
  const [facets, setFacets] = useState<ICourseSearchData["facets"]>(EMPTY_FACETS);

  useEffect(() => {
    if (searchKey !== canonicalKey) {
      setSearchParams(new URLSearchParams(canonicalKey), { replace: true });
    }
  }, [canonicalKey, searchKey, setSearchParams]);

  const updateState = useCallback(
    (patch: Partial<SearchState>, replace = false) => {
      setSearchParams(searchStateToParams({ ...state, ...patch }), { replace });
    },
    [setSearchParams, state],
  );

  const handlePageChange = useCallback(
    (page: number) => updateState({ page }),
    [updateState],
  );
  const handlePageCorrection = useCallback(
    (page: number) => updateState({ page }, true),
    [updateState],
  );

  return (
    <main className="grid w-full gap-8 px-4 py-8 sm:px-8 md:grid-cols-[18rem_1fr] lg:px-16">
      <SearchBox
        key={state.q}
        initialQuery={state.q}
        onSearch={(query) => updateState({ q: query, page: 1 })}
      />

      <SearchFilters
        state={state}
        facets={facets}
        onChange={(patch) => updateState(patch)}
        onClear={() => setSearchParams(new URLSearchParams())}
      />

      {searchKey === canonicalKey ? (
        <SearchResults
          key={canonicalKey}
          state={state}
          onPageChange={handlePageChange}
          onPageCorrection={handlePageCorrection}
          onFacetsReady={setFacets}
        />
      ) : (
        <section className="grid min-h-64 place-items-center" aria-busy="true">
          <Spinner size="lg" label="Normalizando busca" />
        </section>
      )}
    </main>
  );
}
