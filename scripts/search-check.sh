#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
EXPLORE="$ROOT/frontend/src/pages/Publico/Explore/index.tsx"
STATE="$ROOT/frontend/src/pages/Publico/Explore/searchState.ts"
BACKEND_ROUTER="$ROOT/backend/backend/app/routers/search.py"
MIDDLEWARE="$ROOT/backend/backend/app/core/middleware.py"

for file in "$EXPLORE" "$STATE" "$BACKEND_ROUTER" "$MIDDLEWARE"; do
  test -f "$file"
done

grep -q 'url: "/search/courses"' "$EXPLORE"
grep -q 'useSearchParams' "$EXPLORE"
grep -q 'searchStateToParams' "$EXPLORE"
grep -q 'buildSearchRequestParams' "$EXPLORE"

for key in category_id level_id instructor_id price sort order page page_size; do
  grep -q "$key" "$STATE"
done

grep -q 'Query(default=12, ge=1, le=48)' "$BACKEND_ROUTER"
grep -q 'Literal\["title", "price", "rating", "newest"\]' "$BACKEND_ROUTER"
grep -q '"/search/courses"' "$MIDDLEWARE"

if grep -q 'api.get<ICursos\[\]>' "$EXPLORE"; then
  echo "Explore ainda carrega o catálogo inteiro para filtrar no navegador." >&2
  exit 1
fi

if grep -q 'visibleCourses' "$EXPLORE"; then
  echo "Filtro client-side legado ainda está presente." >&2
  exit 1
fi

echo "Advanced Search structural check passed."
