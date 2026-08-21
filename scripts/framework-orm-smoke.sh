#!/bin/sh
set -eu

BASE_URL="${BASE_URL:-https://localhost}"

info() {
    printf '\n==> %s\n' "$1"
}

info "Checking React entrypoint through HTTPS"
curl --silent --show-error --fail --insecure "$BASE_URL/" >/dev/null
curl --silent --show-error --fail --insecure "$BASE_URL/explorar" >/dev/null

info "Checking FastAPI through the reverse proxy"
curl --silent --show-error --fail --insecure "$BASE_URL/api/status" \
    | grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"'
curl --silent --show-error --fail --insecure "$BASE_URL/api/categories/" \
    | grep -Eq '"data"[[:space:]]*:'

info "Checking Alembic single-head state"
docker compose exec -T backend alembic heads | tee /tmp/framework-orm-heads.txt
test "$(grep -c '(head)' /tmp/framework-orm-heads.txt)" -eq 1
docker compose exec -T backend alembic current | grep -q '(head)'

info "Running focused Framework/ORM integration tests"
docker compose exec -T backend pytest -q \
    tests/test_orm_architecture.py \
    tests/test_framework_orm_integration.py

info "Framework/ORM smoke passed."
