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

command -v git >/dev/null 2>&1 || fail "git is required"
command -v docker >/dev/null 2>&1 || fail "docker is required"
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required"

info "Checking tracked secret files"
TRACKED_ENV=$(git ls-files | grep -E '(^|/)\.env($|\.)' | grep -vE '(^|/)\.env\.example$' || true)
[ -z "$TRACKED_ENV" ] || fail "tracked environment files found:\n$TRACKED_ENV"

TRACKED_KEYS=$(git ls-files | grep -Ei '\.(key|pem)$' || true)
[ -z "$TRACKED_KEYS" ] || fail "tracked private-key-like files found:\n$TRACKED_KEYS"

info "Running clean-install deployment smoke"
sh scripts/clean-install-smoke.sh

info "Running backend regression suite inside the deployed backend image"
docker compose exec -T backend pytest

info "Verifying Alembic has a single head and database is current"
HEAD_COUNT=$(docker compose exec -T backend sh -c "alembic heads | grep -c '(head)'" || true)
[ "$HEAD_COUNT" = "1" ] || fail "expected exactly one Alembic head, got $HEAD_COUNT"
docker compose exec -T backend alembic current | grep -q '(head)' || fail "database is not at Alembic head"

info "Running frontend lint and production build in an isolated Node container"
docker run --rm \
  -v "$ROOT_DIR/frontend:/src:ro" \
  node:22-alpine \
  sh -c 'cp -R /src /tmp/frontend && cd /tmp/frontend && npm ci && npm run lint && npm run build'

info "Checking legal pages through HTTPS"
curl --silent --show-error --fail --insecure https://localhost/privacidade | grep -q '<!doctype html>' || \
  curl --silent --show-error --fail --insecure https://localhost/privacidade >/dev/null
curl --silent --show-error --fail --insecure https://localhost/termos | grep -q '<!doctype html>' || \
  curl --silent --show-error --fail --insecure https://localhost/termos >/dev/null

info "Git author summary for human participation review"
git shortlog -sne --all

cat <<'EOF'

Automated mandatory gate passed.

The project is NOT automatically evaluation-ready yet. Complete and sign off the manual checklist in:

  docs/evaluation/MANDATORY_CHECKLIST.md

Required human checks include stable Chrome Console/Network, responsive/device review,
two simultaneous users, legal-text relevance, team participation evidence and a final clean-clone rehearsal.
EOF
