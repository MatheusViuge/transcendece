#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

info() {
  printf '\n==> %s\n' "$1"
}

command -v docker >/dev/null 2>&1 || fail "docker is required"
command -v curl >/dev/null 2>&1 || fail "curl is required"
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required"

[ -f .env ] || fail ".env is missing. Run: cp .env.example .env and replace the example secrets."

if grep -q 'change-me-local-db-password' .env || grep -q 'change-me-with-a-long-random-secret' .env; then
  fail ".env still contains example secrets. Replace them before starting the stack."
fi

info "Validating Docker Compose configuration"
docker compose config >/dev/null

info "Building backend image"
docker compose build backend

info "Building frontend image"
docker compose build frontend

info "Building reverse proxy image"
docker compose build proxy

info "Starting the full stack"
docker compose up -d

info "Waiting for the HTTPS API health endpoint"
ATTEMPTS=0
until curl --silent --show-error --fail --insecure https://localhost/api/status >/tmp/transcendece-status.json 2>/dev/null; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge 60 ]; then
    docker compose ps >&2 || true
    docker compose logs --tail=120 backend proxy >&2 || true
    fail "stack did not become healthy within the smoke-test window"
  fi
  sleep 2
done

grep -q '"status":"ok"' /tmp/transcendece-status.json || \
  grep -q '"status": "ok"' /tmp/transcendece-status.json || \
  fail "unexpected /api/status response"
rm -f /tmp/transcendece-status.json

info "Checking HTTP to HTTPS redirect"
HTTP_HEADERS=$(curl --silent --show-error --head http://localhost)
printf '%s\n' "$HTTP_HEADERS" | grep -Eq '^HTTP/[0-9.]+ 30[1278]' || fail "HTTP endpoint did not return a redirect"
printf '%s\n' "$HTTP_HEADERS" | grep -Eiq '^location: https://localhost/?' || fail "HTTP redirect does not point to HTTPS"

info "Checking frontend over HTTPS"
curl --silent --show-error --fail --insecure https://localhost/ >/dev/null
curl --silent --show-error --fail --insecure https://localhost/login >/dev/null
curl --silent --show-error --fail --insecure https://localhost/privacidade >/dev/null
curl --silent --show-error --fail --insecure https://localhost/termos >/dev/null

info "Checking internal service exposure"
if curl --silent --connect-timeout 2 http://localhost:8000/status >/dev/null 2>&1; then
  fail "backend is unexpectedly exposed directly on localhost:8000"
fi
if curl --silent --connect-timeout 2 http://localhost:8080/ >/dev/null 2>&1; then
  fail "frontend is unexpectedly exposed directly on localhost:8080"
fi

info "Checking Alembic revision"
CURRENT=$(docker compose exec -T backend alembic current)
HEADS=$(docker compose exec -T backend alembic heads)
printf '%s\n' "$CURRENT"
printf '%s\n' "$HEADS"
printf '%s\n' "$CURRENT" | grep -q '(head)' || fail "database is not at Alembic head"

info "Checking container health"
docker compose ps
UNHEALTHY=$(docker compose ps --status unhealthy --quiet)
if [ -n "$UNHEALTHY" ]; then
  printf '%s\n' "$UNHEALTHY" >&2
  fail "one or more containers are unhealthy"
fi

cat <<'EOF'

Clean-install smoke checks passed.

Manual mandatory checks still required before closing Issue #20:
- create/register a real test user;
- log in and navigate authenticated routes;
- verify persistence after `docker compose down` + `docker compose up -d`;
- inspect Chrome Console/Network;
- run the documented multi-user scenario.

The script intentionally leaves the stack running for those checks.
EOF
