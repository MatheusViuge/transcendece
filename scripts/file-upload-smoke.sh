#!/bin/sh
set -eu

BASE_URL=${BASE_URL:-https://localhost}
PASSWORD=${SEED_PASSWORD:-SearchSeed42!}

login() {
  email=$1
  curl --silent --show-error --fail --insecure \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$email\",\"senha\":\"$PASSWORD\"}" \
    "$BASE_URL/api/auth/login" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["data"]["access_token"])'
}

ALICE_TOKEN=$(login alice.ferreira@seed.example.com)
CAMILA_TOKEN=$(login camila.nunes@seed.example.com)

python - <<'PY'
from pathlib import Path
Path('/tmp/file-upload-smoke.png').write_bytes(b'\x89PNG\r\n\x1a\nfile-upload-smoke')
Path('/tmp/file-upload-fake.jpg').write_bytes(b'\x89PNG\r\n\x1a\nwrong-extension')
PY

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -F 'purpose=ci-smoke' \
  -F 'file=@/tmp/file-upload-smoke.png;type=image/png' \
  "$BASE_URL/api/files" -o /tmp/file-upload-created.json

FILE_ID=$(python - <<'PY'
import json
with open('/tmp/file-upload-created.json', encoding='utf-8') as handle:
    print(json.load(handle)['data']['id'])
PY
)

test -n "$FILE_ID"

owner_status=$(curl --silent --output /tmp/file-upload-owner.bin --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/files/$FILE_ID/content")
test "$owner_status" = "200"

other_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $CAMILA_TOKEN" \
  "$BASE_URL/api/files/$FILE_ID/content")
test "$other_status" = "403"

invalid_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -F 'purpose=ci-smoke' \
  -F 'file=@/tmp/file-upload-fake.jpg;type=image/png' \
  "$BASE_URL/api/files")
test "$invalid_status" = "422"

# The storage must survive an application container restart.
docker compose restart backend >/dev/null
for attempt in $(seq 1 45); do
  if curl --silent --show-error --fail --insecure "$BASE_URL/api/status" | grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"'; then
    break
  fi
  [ "$attempt" -eq 45 ] && exit 1
  sleep 2
done

ALICE_TOKEN=$(login alice.ferreira@seed.example.com)
after_restart=$(curl --silent --output /tmp/file-upload-after-restart.bin --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/files/$FILE_ID/content")
test "$after_restart" = "200"
cmp /tmp/file-upload-owner.bin /tmp/file-upload-after-restart.bin

curl --silent --show-error --fail --insecure \
  -X DELETE \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/files/$FILE_ID" >/dev/null

removed_status=$(curl --silent --output /dev/null --write-out '%{http_code}' --insecure \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  "$BASE_URL/api/files/$FILE_ID/content")
test "$removed_status" = "404"

echo "File Upload external HTTPS persistence/ownership smoke passed."
