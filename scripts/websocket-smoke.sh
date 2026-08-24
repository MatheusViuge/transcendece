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
  test "$status" = "200" || { cat "$body" >&2; rm -f "$body"; exit 1; }
  python - "$body" <<'PY'
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
    "$BASE_URL/api/users/me" | python -c 'import json,sys; print(json.load(sys.stdin)["data"]["id"])'
}

ALICE_TOKEN=$(login alice.ferreira@seed.example.com)
CAMILA_TOKEN=$(login camila.nunes@seed.example.com)
CAMILA_ID=$(user_id "$CAMILA_TOKEN")

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"recipient_id\":$CAMILA_ID}" \
  "$BASE_URL/api/chat/conversations" -o /tmp/ws-conversation.json
CONVERSATION_ID=$(python - <<'PY'
import json
with open('/tmp/ws-conversation.json', encoding='utf-8') as handle:
    print(json.load(handle)['data']['id'])
PY
)

# Run the actual WSS clients from the backend container. The image carries the
# same `websockets` runtime dependency used by Uvicorn, and the connection goes
# through the HTTPS Nginx proxy to exercise Upgrade headers end-to-end.
docker compose exec -T \
  -e ALICE_TOKEN="$ALICE_TOKEN" \
  -e CAMILA_TOKEN="$CAMILA_TOKEN" \
  -e CONVERSATION_ID="$CONVERSATION_ID" \
  backend python - <<'PY'
import asyncio
import json
import os
import ssl
import urllib.request

import websockets

URI = "wss://proxy/api/ws/chat"
REST_BASE = "https://proxy/api"
ALICE_TOKEN = os.environ["ALICE_TOKEN"]
CAMILA_TOKEN = os.environ["CAMILA_TOKEN"]
CONVERSATION_ID = int(os.environ["CONVERSATION_ID"])
SSL = ssl.create_default_context()
SSL.check_hostname = False
SSL.verify_mode = ssl.CERT_NONE


def rest_message(token: str, content: str) -> dict:
    request = urllib.request.Request(
        f"{REST_BASE}/chat/conversations/{CONVERSATION_ID}/messages",
        data=json.dumps({"content": content}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, context=SSL, timeout=10) as response:
        return json.loads(response.read().decode())["data"]


def recover(token: str, after_id: int) -> list[dict]:
    request = urllib.request.Request(
        f"{REST_BASE}/chat/conversations/{CONVERSATION_ID}/messages?after_id={after_id}&limit=100",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, context=SSL, timeout=10) as response:
        return json.loads(response.read().decode())["data"]["items"]


async def authenticate(socket, token: str) -> None:
    await socket.send(json.dumps({"type": "auth", "token": token}))
    ready = json.loads(await asyncio.wait_for(socket.recv(), timeout=5))
    assert ready["event"] == "realtime.ready", ready


async def main() -> None:
    async with websockets.connect(URI, ssl=SSL, open_timeout=10) as alice, websockets.connect(URI, ssl=SSL, open_timeout=10) as camila:
        await authenticate(alice, ALICE_TOKEN)
        await authenticate(camila, CAMILA_TOKEN)
        sent = await asyncio.to_thread(rest_message, ALICE_TOKEN, "WSS smoke realtime")
        event_a = json.loads(await asyncio.wait_for(alice.recv(), timeout=5))
        event_c = json.loads(await asyncio.wait_for(camila.recv(), timeout=5))
        assert event_a["id"] == sent["id"], (event_a, sent)
        assert event_c["id"] == sent["id"], (event_c, sent)
        first_id = sent["id"]

    # Gap recovery after disconnect is REST-backed and idempotent by message ID.
    await asyncio.to_thread(rest_message, ALICE_TOKEN, "WSS smoke gap 1")
    await asyncio.to_thread(rest_message, ALICE_TOKEN, "WSS smoke gap 2")
    recovered = await asyncio.to_thread(recover, CAMILA_TOKEN, first_id)
    assert [item["content"] for item in recovered] == ["WSS smoke gap 1", "WSS smoke gap 2"], recovered

    # Reconnect and keepalive frame complete the graceful lifecycle gate.
    async with websockets.connect(URI, ssl=SSL, open_timeout=10) as camila:
        await authenticate(camila, CAMILA_TOKEN)
        await camila.send(json.dumps({"type": "ping"}))
        pong = json.loads(await asyncio.wait_for(camila.recv(), timeout=5))
        assert pong == {"event": "realtime.pong"}, pong


asyncio.run(main())
PY

printf '%s\n' 'WebSocket WSS multi-client/reconnect smoke passed.'
