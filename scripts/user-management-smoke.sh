#!/bin/sh
set -eu

BASE_URL=${BASE_URL:-https://localhost}
PASSWORD=${SEED_PASSWORD:-SearchSeed42!}

login() {
  email=$1
  body=$(mktemp)
  status=$(curl --silent --show-error --insecure --output "$body" --write-out '%{http_code}' \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$email\",\"senha\":\"$PASSWORD\"}" \
    "$BASE_URL/api/auth/login")
  if [ "$status" != "200" ]; then
    printf 'User Management smoke login failed for %s: HTTP %s\n' "$email" "$status" >&2
    cat "$body" >&2
    rm -f "$body"
    exit 1
  fi
  python - "$body" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    print(json.load(handle)['data']['access_token'])
PY
  rm -f "$body"
}

ALICE_TOKEN=$(login alice.ferreira@seed.example.com)
CAMILA_TOKEN=$(login camila.nunes@seed.example.com)

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/me" -o /tmp/um-alice.json
read -r ALICE_ID ALICE_CODE <<EOF
$(python - <<'PY'
import json, re
with open('/tmp/um-alice.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert data['email'] == 'alice.ferreira@seed.example.com'
assert data['avatar_url'] == '/default-avatar.svg'
assert re.fullmatch(r'[A-Z2-9]{5}-[A-Z2-9]{5}', data['friend_code'])
print(data['id'], data['friend_code'])
PY
)
EOF

default_avatar_status=$(curl --silent --show-error --insecure --output /dev/null --write-out '%{http_code}' \
  "$BASE_URL/api/users/$ALICE_ID/avatar")
test "$default_avatar_status" = "307"

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/me" -o /tmp/um-camila.json
CAMILA_ID=$(python - <<'PY'
import json
with open('/tmp/um-camila.json', encoding='utf-8') as handle:
    print(json.load(handle)['data']['id'])
PY
)

curl --silent --show-error --fail --insecure -X PATCH \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Alice","sobrenome":"Ferreira"}' \
  "$BASE_URL/api/users/me" >/dev/null

protected_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure -X PATCH \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tipo_usuario":"admin"}' \
  "$BASE_URL/api/users/me")
test "$protected_status" = "422"

curl --silent --show-error --fail --insecure -X POST \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/presence/heartbeat" >/dev/null

# Presence is private before friendship consent.
curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/$ALICE_ID" -o /tmp/um-public-before.json
python - <<'PY'
import json
with open('/tmp/um-public-before.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert data['online'] is None
assert 'email' not in data
assert 'data_nascimento' not in data
PY

COMPACT_CODE=$(printf '%s' "$ALICE_CODE" | tr -d '-')
curl --silent --show-error --fail --insecure \
  -G -H "Authorization: Bearer $CAMILA_TOKEN" \
  --data-urlencode "q=$COMPACT_CODE" \
  "$BASE_URL/api/users" -o /tmp/um-code-search.json
python - "$ALICE_ID" "$ALICE_CODE" <<'PY'
import json, sys
with open('/tmp/um-code-search.json', encoding='utf-8') as handle:
    rows = json.load(handle)['data']
assert len(rows) == 1
assert rows[0]['id'] == int(sys.argv[1])
assert rows[0]['friend_code'] == sys.argv[2]
assert rows[0]['online'] is None
assert 'email' not in rows[0]
PY

self_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure -X POST \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/friend-requests/$ALICE_ID")
test "$self_status" = "422"

curl --silent --show-error --fail --insecure -X POST \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/friend-requests/$CAMILA_ID" >/dev/null

# A request alone must not create friendship.
curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/friends" -o /tmp/um-before-accept.json
python - <<'PY'
import json
with open('/tmp/um-before-accept.json', encoding='utf-8') as handle:
    assert json.load(handle)['data'] == []
PY

inverse_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure -X POST \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/friend-requests/$ALICE_ID")
test "$inverse_status" = "409"

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/friend-requests" -o /tmp/um-requests.json
python - "$ALICE_ID" <<'PY'
import json, sys
with open('/tmp/um-requests.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert [row['user']['id'] for row in data['incoming']] == [int(sys.argv[1])]
assert data['incoming'][0]['user']['online'] is None
PY

curl --silent --show-error --fail --insecure -X POST \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/friend-requests/$ALICE_ID/accept" >/dev/null

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/friends" -o /tmp/um-friends.json
python - "$ALICE_ID" <<'PY'
import json, sys
alice_id = int(sys.argv[1])
with open('/tmp/um-friends.json', encoding='utf-8') as handle:
    friends = json.load(handle)['data']
alice = next(item for item in friends if item['id'] == alice_id)
assert alice['online'] is True
assert 'email' not in alice
assert 'data_nascimento' not in alice
PY

python - <<'PY'
from pathlib import Path
Path('/tmp/um-avatar.png').write_bytes(b'\x89PNG\r\n\x1a\nuser-management-smoke')
PY
curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -F 'purpose=avatar' \
  -F 'file=@/tmp/um-avatar.png;type=image/png' \
  "$BASE_URL/api/files" -o /tmp/um-upload.json
FILE_ID=$(python - <<'PY'
import json
with open('/tmp/um-upload.json', encoding='utf-8') as handle:
    print(json.load(handle)['data']['id'])
PY
)

curl --silent --show-error --fail --insecure -X PUT \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/me/avatar/$FILE_ID" -o /tmp/um-avatar-selected.json
python - "$ALICE_ID" <<'PY'
import json, sys
with open('/tmp/um-avatar-selected.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert data['avatar_url'] == f'/api/users/{sys.argv[1]}/avatar'
PY

curl --silent --show-error --fail --insecure \
  "$BASE_URL/api/users/$ALICE_ID/avatar" -o /tmp/um-avatar-returned.png
cmp /tmp/um-avatar.png /tmp/um-avatar-returned.png

curl --silent --show-error --fail --insecure -X DELETE \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/users/me/avatar" -o /tmp/um-avatar-removed.json
python - <<'PY'
import json
with open('/tmp/um-avatar-removed.json', encoding='utf-8') as handle:
    assert json.load(handle)['data']['avatar_url'] == '/default-avatar.svg'
PY

curl --silent --show-error --fail --insecure -X DELETE \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/friends/$ALICE_ID" >/dev/null

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/users/$ALICE_ID" -o /tmp/um-public-after-remove.json
python - <<'PY'
import json
with open('/tmp/um-public-after-remove.json', encoding='utf-8') as handle:
    assert json.load(handle)['data']['online'] is None
PY

echo "Standard User Management HTTPS friendship-consent/friend-code/privacy smoke passed."
