import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { Button } from "@/components/Button";
import { BaseInput } from "@/components/Form";
import { Alert, Pagination, Spinner } from "@/design-system";
import type { ICourseSearchData } from "@/interfaces/cursos";
import { api, catchCustom } from "@/services/api";
import { searchSchema } from "@/pages/Publico/schemas/searchSchema";

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

  const [queryInput, setQueryInput] = useState(state.q);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [result, setResult] = useState<ICourseSearchData | null>(null);
  const [loading, setLoading] = useState(true);
  const [requestError, setRequestError] = useState<string | null>(null);

  useEffect(() => {
    if (searchKey !== canonicalKey) {
      setSearchParams(new URLSearchParams(canonicalKey), { replace: true });
    }
  }, [canonicalKey, searchKey, setSearchParams]);

  useEffect(() => {
    setQueryInput(state.q);
  }, [state.q]);

  useEffect(() => {
    if (searchKey !== canonicalKey) return;

    let active = true;
    setLoading(true);
    setRequestError(null);

    api.get<ICourseSearchData>({
      url: "/search/courses",
      config: { params: buildSearchRequestParams(state) },
      hiddenToast: true,
    })
      .then((response) => {
        if (!active) return;

        const maxPage = Math.max(response.data.pagination.total_pages, 1);
        if (state.page > maxPage) {
          setSearchParams(
            searchStateToParams({ ...state, page: maxPage }),
            { replace: true },
          );
          return;
        }

        setResult(response.data);
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
  }, [canonicalKey, searchKey, setSearchParams, state]);

  const updateState = (patch: Partial<SearchState>) => {
    setSearchParams(searchStateToParams({ ...state, ...patch }));
  };

  const onSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const parsed = searchSchema.safeParse({ busca: queryInput });

    if (!parsed.success) {
      setQueryError(parsed.error.issues[0]?.message ?? "Busca inválida.");
      return;
    }

    setQueryError(null);
    updateState({ q: parsed.data.busca, page: 1 });
  };

  const facets = result?.facets ?? EMPTY_FACETS;
  const pagination = result?.pagination;

  return (
    <main className="grid w-full gap-8 px-4 py-8 sm:px-8 md:grid-cols-[18rem_1fr] lg:px-16">
      <form onSubmit={onSearch} className="col-span-full grid gap-2 lg:grid-cols-[minmax(0,42rem)_auto] lg:items-start">
        <div className="grid gap-1">
          <label htmlFor="buscar" className="text-sm font-medium text-text">Buscar cursos</label>
          <BaseInput
            id="buscar"
            value={queryInput}
            onChange={(event) => setQueryInput(event.target.value)}
            placeholder="Título, descrição, categoria, nível ou instrutor..."
            maxLength={120}
            aria-invalid={Boolean(queryError)}
          />
          {queryError && <p className="text-xs text-danger" role="alert">{queryError}</p>}
        </div>
        <Button type="submit" variant="accent" className="lg:mt-6">Buscar</Button>
      </form>

      <SearchFilters
        state={state}
        facets={facets}
        onChange={updateState}
        onClear={() => setSearchParams(new URLSearchParams())}
      />

      <section className="min-w-0" aria-busy={loading}>
        {requestError && (
          <Alert tone="danger" title="Erro na busca" className="mb-5">
            {requestError}
          </Alert>
        )}

        {loading && !result ? (
          <div className="grid min-h-64 place-items-center">
            <Spinner size="lg" label="Buscando cursos" />
          </div>
        ) : result && result.items.length > 0 ? (
          <div className="grid gap-6">
            <CoursesCount count={result.pagination.total} />
            <CoursesGrid courses={result.items} />
            {pagination && (
              <Pagination
                page={pagination.page}
                totalPages={pagination.total_pages}
                onPageChange={(page) => updateState({ page })}
              />
            )}
          </div>
        ) : !requestError ? (
          <EmptyState />
        ) : null}
      </section>
    </main>
  );
}
