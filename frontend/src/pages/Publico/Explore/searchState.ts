export type SearchSort = "title" | "price" | "rating" | "newest";
export type SearchOrder = "asc" | "desc";
export type SearchPrice = "free" | "paid";

export type SearchState = {
  q: string;
  categoryId: number | null;
  levelId: number | null;
  instructorId: number | null;
  price: SearchPrice | null;
  sort: SearchSort;
  order: SearchOrder;
  page: number;
  pageSize: number;
};

const SORT_VALUES = new Set<SearchSort>(["title", "price", "rating", "newest"]);
const ORDER_VALUES = new Set<SearchOrder>(["asc", "desc"]);
const PRICE_VALUES = new Set<SearchPrice>(["free", "paid"]);

function positiveInt(value: string | null): number | null {
  if (!value || !/^\d+$/.test(value)) return null;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null;
}

export function readSearchState(params: URLSearchParams): SearchState {
  const rawQuery = (params.get("q") ?? "").trim().slice(0, 120);
  const rawSort = params.get("sort") as SearchSort | null;
  const rawOrder = params.get("order") as SearchOrder | null;
  const rawPrice = params.get("price") as SearchPrice | null;
  const rawPageSize = positiveInt(params.get("page_size"));

  return {
    q: rawQuery,
    categoryId: positiveInt(params.get("category")),
    levelId: positiveInt(params.get("level")),
    instructorId: positiveInt(params.get("instructor")),
    price: rawPrice && PRICE_VALUES.has(rawPrice) ? rawPrice : null,
    sort: rawSort && SORT_VALUES.has(rawSort) ? rawSort : "newest",
    order: rawOrder && ORDER_VALUES.has(rawOrder) ? rawOrder : "desc",
    page: positiveInt(params.get("page")) ?? 1,
    pageSize: rawPageSize && rawPageSize <= 48 ? rawPageSize : 12,
  };
}

export function searchStateToParams(state: SearchState): URLSearchParams {
  const params = new URLSearchParams();

  if (state.q) params.set("q", state.q);
  if (state.categoryId) params.set("category", String(state.categoryId));
  if (state.levelId) params.set("level", String(state.levelId));
  if (state.instructorId) params.set("instructor", String(state.instructorId));
  if (state.price) params.set("price", state.price);
  if (state.sort !== "newest") params.set("sort", state.sort);
  if (state.order !== "desc") params.set("order", state.order);
  if (state.page > 1) params.set("page", String(state.page));
  if (state.pageSize !== 12) params.set("page_size", String(state.pageSize));

  return params;
}

export function buildSearchRequestParams(state: SearchState) {
  return {
    q: state.q || undefined,
    category_id: state.categoryId ?? undefined,
    level_id: state.levelId ?? undefined,
    instructor_id: state.instructorId ?? undefined,
    price: state.price ?? undefined,
    sort: state.sort,
    order: state.order,
    page: state.page,
    page_size: state.pageSize,
  };
}
