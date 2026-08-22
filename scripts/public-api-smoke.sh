#!/bin/sh
set -eu

BASE_URL=${BASE_URL:-https://localhost/api}
CURL="curl --silent --show-error --insecure"

$CURL --fail "$BASE_URL/openapi.json" > /tmp/public-api-openapi.json
python - <<'PY'
import json

with open('/tmp/public-api-openapi.json', encoding='utf-8') as handle:
    document = json.load(handle)

paths = document['paths']
assert '/v1/public/courses' in paths
assert {'get', 'post'}.issubset(paths['/v1/public/courses'])
assert {'get', 'put', 'delete'}.issubset(paths['/v1/public/courses/{course_id}'])
assert '/keys' in paths

scheme = document['components']['securitySchemes']['APIKeyHeader']
assert scheme['type'] == 'apiKey'
assert scheme['in'] == 'header'
assert scheme['name'] == 'X-API-Key'
PY

$CURL --fail -H 'Content-Type: application/json' \
  -d '{"email":"ana.ribeiro@seed.example.com","senha":"SearchSeed42!"}' \
  "$BASE_URL/auth/login" > /tmp/public-api-login.json
TOKEN=$(python -c 'import json; print(json.load(open("/tmp/public-api-login.json"))["data"]["access_token"])')

$CURL --fail -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"ci-public-api","scopes":["courses:read","courses:write"]}' \
  "$BASE_URL/keys" > /tmp/public-api-key.json
API_KEY=$(python -c 'import json; print(json.load(open("/tmp/public-api-key.json"))["data"]["secret"])')
KEY_ID=$(python -c 'import json; print(json.load(open("/tmp/public-api-key.json"))["data"]["id"])')

missing=$($CURL --output /dev/null --write-out '%{http_code}' "$BASE_URL/v1/public/courses")
test "$missing" = "401"

$CURL --fail -H "X-API-Key: $API_KEY" \
  "$BASE_URL/v1/public/courses?page=1&page_size=5" > /tmp/public-api-courses.json
python - <<'PY'
import json
data = json.load(open('/tmp/public-api-courses.json', encoding='utf-8'))['data']
assert len(data['items']) == 5
assert data['pagination']['total'] >= 30
PY
CATEGORY_ID=$(python -c 'import json; print(json.load(open("/tmp/public-api-courses.json"))["data"]["items"][0]["category"]["id"])')
LEVEL_ID=$(python -c 'import json; print(json.load(open("/tmp/public-api-courses.json"))["data"]["items"][0]["level"]["id"])')

$CURL --fail -X POST -H "X-API-Key: $API_KEY" -H 'Content-Type: application/json' \
  -d "{\"title\":\"CI Public API Course\",\"description\":\"Created through external Public API smoke.\",\"price\":42,\"workload_hours\":8,\"category_id\":$CATEGORY_ID,\"level_id\":$LEVEL_ID}" \
  "$BASE_URL/v1/public/courses" > /tmp/public-api-created.json
COURSE_ID=$(python -c 'import json; d=json.load(open("/tmp/public-api-created.json"))["data"]; assert d["instructor"]["name"] == "Ana Ribeiro"; print(d["id"])')

$CURL --fail -H "X-API-Key: $API_KEY" "$BASE_URL/v1/public/courses/$COURSE_ID" >/dev/null
$CURL --fail -X PUT -H "X-API-Key: $API_KEY" -H 'Content-Type: application/json' \
  -d '{"title":"CI Public API Course Updated","price":84}' \
  "$BASE_URL/v1/public/courses/$COURSE_ID" > /tmp/public-api-updated.json
python -c 'import json; d=json.load(open("/tmp/public-api-updated.json"))["data"]; assert d["title"] == "CI Public API Course Updated" and d["price"] == 84.0'

deleted=$($CURL --output /dev/null --write-out '%{http_code}' -X DELETE -H "X-API-Key: $API_KEY" "$BASE_URL/v1/public/courses/$COURSE_ID")
test "$deleted" = "204"

$CURL --fail -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"ci-rate-limit","scopes":["courses:read"]}' \
  "$BASE_URL/keys" > /tmp/public-api-rate-key.json
RATE_KEY=$(python -c 'import json; print(json.load(open("/tmp/public-api-rate-key.json"))["data"]["secret"])')
for _ in $(seq 1 20); do
  code=$($CURL --output /dev/null --write-out '%{http_code}' -H "X-API-Key: $RATE_KEY" "$BASE_URL/v1/public/courses?page_size=1")
  test "$code" = "200"
done
limited=$($CURL --dump-header /tmp/public-api-rate-headers.txt --output /dev/null --write-out '%{http_code}' -H "X-API-Key: $RATE_KEY" "$BASE_URL/v1/public/courses?page_size=1")
test "$limited" = "429"
grep -Eiq '^x-ratelimit-limit:[[:space:]]*20' /tmp/public-api-rate-headers.txt
grep -Eiq '^x-ratelimit-remaining:[[:space:]]*0' /tmp/public-api-rate-headers.txt
grep -Eiq '^retry-after:[[:space:]]*[1-9][0-9]*' /tmp/public-api-rate-headers.txt

$CURL --fail -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE_URL/keys/$KEY_ID" >/dev/null
revoked=$($CURL --output /dev/null --write-out '%{http_code}' -H "X-API-Key: $API_KEY" "$BASE_URL/v1/public/courses")
test "$revoked" = "401"

echo "Public API external HTTPS smoke passed."
