#!/bin/sh
set -eu

BASE_URL=${BASE_URL:-https://localhost/api}
CURL="curl --silent --show-error --insecure"
PASSWORD='SearchSeed42!'
TEMP_EMAIL='ci.rbac.user@seed.example.com'
TEMP_PASSWORD='Rbac42!'

login() {
  email=$1
  password=$2
  output=$3
  $CURL --fail -H 'Content-Type: application/json' \
    -d "{\"email\":\"$email\",\"senha\":\"$password\"}" \
    "$BASE_URL/auth/login" > "$output"
  python -c "import json; print(json.load(open('$output'))['data']['access_token'])"
}

ADMIN_TOKEN=$(login 'admin.rbac@seed.example.com' "$PASSWORD" /tmp/rbac-admin-login.json)
STUDENT_TOKEN=$(login 'alice.ferreira@seed.example.com' "$PASSWORD" /tmp/rbac-student-login.json)

student_admin_status=$($CURL --output /dev/null --write-out '%{http_code}' \
  -H "Authorization: Bearer $STUDENT_TOKEN" "$BASE_URL/admin/users")
test "$student_admin_status" = "403"

$CURL --fail -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/admin/users?page=1&page_size=5&q=alice" > /tmp/rbac-users.json
python - <<'PY'
import json
payload = json.load(open('/tmp/rbac-users.json', encoding='utf-8'))
data = payload['data']
assert data['pagination']['total'] == 1, data['pagination']
assert data['items'][0]['email'] == 'alice.ferreira@seed.example.com'
raw = json.dumps(payload).lower()
assert 'senha_hash' not in raw
assert 'api_key' not in raw
PY

$CURL --fail -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/admin/specialties" > /tmp/rbac-specialties.json
SPECIALTY_ID=$(python -c 'import json; print(json.load(open("/tmp/rbac-specialties.json"))["data"][0]["id"])')

# The CI database is disposable; if a previous retry created this email, find and reuse it.
$CURL --fail -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/admin/users?q=ci.rbac.user%40seed.example.com&page_size=100" > /tmp/rbac-existing.json
EXISTING_ID=$(python - <<'PY'
import json
items = json.load(open('/tmp/rbac-existing.json', encoding='utf-8'))['data']['items']
print(items[0]['id'] if items else '')
PY
)

if [ -n "$EXISTING_ID" ]; then
  USER_ID=$EXISTING_ID
  $CURL --fail -X PATCH -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
    -d '{"is_active":true}' "$BASE_URL/admin/users/$USER_ID/status" >/dev/null
else
  $CURL --fail -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
    -d "{\"nome\":\"CI\",\"sobrenome\":\"RBAC\",\"email\":\"$TEMP_EMAIL\",\"senha\":\"$TEMP_PASSWORD\",\"data_nascimento\":\"1999-01-01\",\"role\":\"aluno\"}" \
    "$BASE_URL/admin/users" > /tmp/rbac-created.json
  USER_ID=$(python -c 'import json; print(json.load(open("/tmp/rbac-created.json"))["data"]["id"])')
fi

$CURL --fail -X PATCH -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"nome":"CI Atualizado"}' "$BASE_URL/admin/users/$USER_ID" > /tmp/rbac-updated.json
python -c 'import json; assert json.load(open("/tmp/rbac-updated.json"))["data"]["nome"] == "CI Atualizado"'

$CURL --fail -X PATCH -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"role\":\"instrutor\",\"especialidade_id\":$SPECIALTY_ID}" \
  "$BASE_URL/admin/users/$USER_ID/role" > /tmp/rbac-role.json
python -c 'import json; assert json.load(open("/tmp/rbac-role.json"))["data"]["tipo_usuario"] == "instrutor"'

$CURL --fail -X PATCH -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"is_active":false}' "$BASE_URL/admin/users/$USER_ID/status" > /tmp/rbac-disabled.json
python -c 'import json; assert json.load(open("/tmp/rbac-disabled.json"))["data"]["is_active"] is False'

disabled_login=$($CURL --output /dev/null --write-out '%{http_code}' -H 'Content-Type: application/json' \
  -d "{\"email\":\"$TEMP_EMAIL\",\"senha\":\"$TEMP_PASSWORD\"}" "$BASE_URL/auth/login")
test "$disabled_login" = "403"

$CURL --fail -H "Authorization: Bearer $ADMIN_TOKEN" "$BASE_URL/auth/me" > /tmp/rbac-me.json
ADMIN_ID=$(python -c 'import json; print(json.load(open("/tmp/rbac-me.json"))["data"]["id"])')
self_lockout=$($CURL --output /dev/null --write-out '%{http_code}' -X PATCH \
  -H "Authorization: Bearer $ADMIN_TOKEN" -H 'Content-Type: application/json' \
  -d '{"is_active":false}' "$BASE_URL/admin/users/$ADMIN_ID/status")
test "$self_lockout" = "409"

$CURL --fail -H "Authorization: Bearer $ADMIN_TOKEN" "$BASE_URL/admin/permissions" >/dev/null

echo "RBAC external HTTPS smoke passed."
