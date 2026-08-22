#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MODEL="$ROOT/backend/backend/app/models/api_key.py"
AUTH="$ROOT/backend/backend/app/core/api_key_auth.py"
ROUTER="$ROOT/backend/backend/app/routers/public_api.py"
KEY_ROUTER="$ROOT/backend/backend/app/routers/api_keys.py"
MIGRATION="$ROOT/backend/backend/alembic/versions_v2/0002_public_api_keys.py"
DOCS="$ROOT/docs/PUBLIC_API.md"

for file in "$MODEL" "$AUTH" "$ROUTER" "$KEY_ROUTER" "$MIGRATION" "$DOCS"; do
  test -f "$file"
done

grep -q 'prefix="/v1/public"' "$ROUTER"
grep -q 'APIKeyHeader' "$AUTH"
grep -q 'name="X-API-Key"' "$AUTH"
grep -q 'with_for_update' "$AUTH"
grep -q 'sha256' "$AUTH"
grep -q 'compare_digest' "$AUTH"
grep -q 'HTTP_429_TOO_MANY_REQUESTS' "$AUTH"
grep -q 'down_revision.*0001_product_baseline' "$MIGRATION"

count=$(grep -Ec '^@router\.(get|post|put|delete)\("/courses' "$ROUTER")
test "$count" -ge 5

for method in get post put delete; do
  grep -q "^@router\\.${method}(\"/courses" "$ROUTER"
done

if grep -Eq 'secret[[:space:]]*=[[:space:]]*Column|api_key[[:space:]]*=[[:space:]]*Column' "$MODEL"; then
  echo "O model de API key parece persistir um secret utilizável em texto puro." >&2
  exit 1
fi

grep -q 'key_hash = Column' "$MODEL"
grep -q 'revoked_at = Column' "$MODEL"
grep -q 'owner_id = Column' "$MODEL"

echo "Public API structural/security check passed."
