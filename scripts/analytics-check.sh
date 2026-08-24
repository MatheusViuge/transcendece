#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

service="$ROOT/backend/backend/app/services/analytics_service.py"
router="$ROOT/backend/backend/app/routers/analytics.py"
frontend="$ROOT/frontend/src/pages/Admin/Analytics/index.tsx"
routes="$ROOT/frontend/src/routes/AppRoutes.tsx"
access="$ROOT/frontend/src/routes/access.ts"
tests="$ROOT/backend/backend/tests/test_analytics.py"
seed="$ROOT/backend/backend/scripts/seed_analytics.py"

for file in "$service" "$router" "$frontend" "$routes" "$access" "$tests" "$seed"; do
  test -f "$file"
done

grep -q 'build_dashboard' "$service"
grep -q 'dashboard_to_csv' "$service"
grep -q 'dashboard_to_pdf' "$service"
grep -q 'DEFAULT_RANGE_DAYS = 30' "$service"
grep -q '@router.get("/dashboard")' "$router"
grep -q '@router.get("/export.csv")' "$router"
grep -q '@router.get("/export.pdf")' "$router"
grep -q '@ws_router.websocket("/ws/analytics")' "$router"
grep -q 'allowed_roles("admin")' "$router"
grep -q 'identity\["role"\] != "admin"' "$router"
grep -q 'analytics.snapshot' "$router"
grep -q 'LineChart' "$frontend"
grep -q 'BarChart' "$frontend"
grep -q 'PieChart' "$frontend"
grep -q 'type="date"' "$frontend"
grep -q 'Exportar CSV' "$frontend"
grep -q 'Exportar PDF' "$frontend"
grep -q 'new WebSocket' "$frontend"
grep -q '/admin/analytics' "$routes"
grep -q 'Analytics.*\/admin\/analytics' "$access"
grep -q 'test_dashboard_is_admin_only_and_uses_real_filtered_data' "$tests"
grep -q 'test_analytics_websocket_is_admin_only_and_pushes_database_changes' "$tests"

printf '%s\n' 'Advanced Analytics structural/security check passed.'
