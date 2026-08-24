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
    printf 'User Interaction smoke login failed for %s: HTTP %s\n' "$email" "$status" >&2
    cat "$body" >&2
    rm -f "$body"
    exit 1
  fi
  python3 - "$body" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    print(json.load(handle)['data']['access_token'])
PY
  rm -f "$body"
}

user_id() {
  token=$1
  curl --silent --show-error --fail --insecure \
    -H "Authorization: Bearer $token" \
    "$BASE_URL/api/users/me" | python3 -c 'import json,sys; print(json.load(sys.stdin)["data"]["id"])'
}

ALICE_TOKEN=$(login alice.ferreira@seed.example.com)
CAMILA_TOKEN=$(login camila.nunes@seed.example.com)
BERNARDO_TOKEN=$(login bernardo.lima@seed.example.com)
ALICE_ID=$(user_id "$ALICE_TOKEN")
CAMILA_ID=$(user_id "$CAMILA_TOKEN")

conversation_status=$(curl --silent --show-error --insecure --output /tmp/ui-conversation.json --write-out '%{http_code}' \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"recipient_id\":$CAMILA_ID}" \
  "$BASE_URL/api/chat/conversations")
case "$conversation_status" in 200|201) ;; *) cat /tmp/ui-conversation.json >&2; exit 1 ;; esac
CONVERSATION_ID=$(python3 - <<'PY'
import json
with open('/tmp/ui-conversation.json', encoding='utf-8') as handle:
    print(json.load(handle)['data']['id'])
PY
)

inverse_status=$(curl --silent --show-error --insecure --output /tmp/ui-inverse.json --write-out '%{http_code}' \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"recipient_id\":$ALICE_ID}" \
  "$BASE_URL/api/chat/conversations")
test "$inverse_status" = "200"
python3 - "$CONVERSATION_ID" <<'PY'
import json, sys
with open('/tmp/ui-inverse.json', encoding='utf-8') as handle:
    assert json.load(handle)['data']['id'] == int(sys.argv[1])
PY

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Alice para Camila - smoke persistente"}' \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages" -o /tmp/ui-message-a.json

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Camila para Alice - resposta persistente"}' \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages" -o /tmp/ui-message-b.json

third_read_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $BERNARDO_TOKEN" \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages")
test "$third_read_status" = "404"

third_write_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $BERNARDO_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"content":"tentativa de intrusão"}' \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages")
test "$third_write_status" = "404"

empty_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"content":"   "}' \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages")
test "$empty_status" = "422"

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages?limit=1" -o /tmp/ui-page.json
python3 - <<'PY'
import json
with open('/tmp/ui-page.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert len(data['items']) == 1
assert data['items'][0]['content'] == 'Camila para Alice - resposta persistente'
assert data['has_more'] is True
assert data['next_before_id'] is not None
PY

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/chat/conversations" -o /tmp/ui-list.json
python3 - "$CAMILA_ID" "$CONVERSATION_ID" <<'PY'
import json, sys
camila_id, conversation_id = map(int, sys.argv[1:])
with open('/tmp/ui-list.json', encoding='utf-8') as handle:
    items = json.load(handle)['data']['items']
row = next(item for item in items if item['id'] == conversation_id)
assert row['participant']['id'] == camila_id
assert row['last_message']['content'] == 'Camila para Alice - resposta persistente'
PY

# Persistence is verified against the real PostgreSQL deployment by restarting only the backend.
docker-compose restart backend >/dev/null
for attempt in $(seq 1 45); do
  if curl --silent --show-error --fail --insecure "$BASE_URL/api/status" | grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"'; then
    break
  fi
  [ "$attempt" -eq 45 ] && { docker-compose logs --tail=120 backend >&2; exit 1; }
  sleep 2
done

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/chat/conversations/$CONVERSATION_ID/messages?limit=10" -o /tmp/ui-after-restart.json
python3 - <<'PY'
import json
with open('/tmp/ui-after-restart.json', encoding='utf-8') as handle:
    contents = [item['content'] for item in json.load(handle)['data']['items']]
assert 'Alice para Camila - smoke persistente' in contents
assert 'Camila para Alice - resposta persistente' in contents
PY

printf '%s\n' 'User Interaction HTTPS multi-user chat/profile/friends persistence smoke passed.'
