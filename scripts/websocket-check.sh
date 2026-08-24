#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

realtime="$ROOT/backend/backend/app/routers/realtime.py"
hub="$ROOT/backend/backend/app/realtime.py"
chat="$ROOT/backend/backend/app/routers/chat.py"
frontend="$ROOT/frontend/src/pages/Chat/index.tsx"
nginx="$ROOT/infra/nginx/nginx.conf"
requirements="$ROOT/backend/requirements.txt"
tests="$ROOT/backend/backend/tests/test_websockets.py"

for file in "$realtime" "$hub" "$chat" "$frontend" "$nginx" "$requirements" "$tests"; do
  test -f "$file"
done

grep -q '@router.websocket("/ws/chat")' "$realtime"
grep -q 'authenticate_realtime_token' "$realtime"
grep -q 'realtime.ready' "$realtime"
grep -q 'realtime.pong' "$realtime"
grep -q 'publish_to_users' "$chat"
grep -q 'after_id' "$chat"
grep -q 'chat.message.created' "$chat"
grep -q 'new WebSocket' "$frontend"
grep -q 'reconnecting' "$frontend"
grep -q 'IntersectionObserver' "$frontend"
grep -q 'mergeMessages' "$frontend"
grep -q 'after_id' "$frontend"
grep -q 'socket.close(1000' "$frontend"
grep -q 'proxy_set_header Upgrade' "$nginx"
grep -q 'proxy_set_header Connection' "$nginx"
grep -q '^websockets==' "$requirements"
grep -q 'test_websocket_broadcast_is_authenticated_and_scoped' "$tests"
grep -q 'test_reconnect_gap_can_be_recovered_with_after_id' "$tests"

printf '%s\n' 'WebSocket structural/security check passed.'
