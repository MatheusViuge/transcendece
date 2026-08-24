#!/bin/sh
set -eu

BASE_URL=${BASE_URL:-https://localhost}
PASSWORD=${SEED_PASSWORD:-SearchSeed42!}
ADMIN_EMAIL=${RBAC_ADMIN_EMAIL:-admin.rbac@seed.example.com}

login_body=$(mktemp)
status=$(curl --silent --show-error --insecure --output "$login_body" --write-out '%{http_code}' \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"senha\":\"$PASSWORD\"}" \
  "$BASE_URL/api/auth/login")
test "$status" = "200" || { cat "$login_body" >&2; rm -f "$login_body"; exit 1; }
ADMIN_TOKEN=$(python - "$login_body" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    print(json.load(handle)['data']['access_token'])
PY
)
rm -f "$login_body"

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/api/analytics/dashboard" -o /tmp/analytics-dashboard.json
python - <<'PY'
import json
with open('/tmp/analytics-dashboard.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert data['kpis']['enrollments'] > 0, data['kpis']
assert data['top_courses'], data
assert data['enrollment_statuses'], data
assert len(data['daily_activity']) == 30, len(data['daily_activity'])
PY

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/api/analytics/dashboard?enrollment_status=concluida" -o /tmp/analytics-completed.json
python - <<'PY'
import json
with open('/tmp/analytics-completed.json', encoding='utf-8') as handle:
    data = json.load(handle)['data']
assert data['kpis']['enrollments'] > 0
assert data['kpis']['completion_rate'] == 100.0, data['kpis']
assert {row['label'] for row in data['enrollment_statuses']} == {'concluida'}
PY

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/api/analytics/export.csv?enrollment_status=ativa" -o /tmp/analytics.csv
grep -q 'Advanced Analytics Dashboard' /tmp/analytics.csv
grep -q 'enrollment_status,ativa' /tmp/analytics.csv

curl --silent --show-error --fail --insecure \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$BASE_URL/api/analytics/export.pdf?enrollment_status=ativa" -o /tmp/analytics.pdf
head -c 8 /tmp/analytics.pdf | grep -q '%PDF-1.4'

# Exercise admin-only realtime snapshots through TLS + Nginx and mutate the real
# PostgreSQL DB while the subscription is active. The next snapshot must change.
docker compose exec -T -e ADMIN_TOKEN="$ADMIN_TOKEN" backend python - <<'PY'
import asyncio
import json
import os
import ssl
from datetime import datetime, timezone

import websockets

from app.database import SessionLocal
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.user import Usuario

URI = 'wss://proxy/api/ws/analytics'
TOKEN = os.environ['ADMIN_TOKEN']
SSL = ssl.create_default_context()
SSL.check_hostname = False
SSL.verify_mode = ssl.CERT_NONE


async def main() -> None:
    async with websockets.connect(URI, ssl=SSL, open_timeout=10) as socket:
        await socket.send(json.dumps({'type': 'auth', 'token': TOKEN}))
        ready = json.loads(await asyncio.wait_for(socket.recv(), timeout=5))
        assert ready['event'] == 'analytics.ready', ready
        await socket.send(json.dumps({'type': 'analytics.subscribe', 'filters': {}}))
        initial = json.loads(await asyncio.wait_for(socket.recv(), timeout=5))
        assert initial['event'] == 'analytics.snapshot', initial
        before = initial['data']['kpis']['enrollments']

        db = SessionLocal()
        try:
            students = db.query(Usuario).filter(Usuario.tipo_usuario == 'aluno').all()
            courses = db.query(Curso).all()
            chosen = None
            for student in students:
                for course in courses:
                    exists = db.query(Matricula).filter(
                        Matricula.aluno_id == student.id,
                        Matricula.curso_id == course.id,
                    ).first()
                    if exists is None:
                        chosen = (student.id, course.id)
                        break
                if chosen:
                    break
            assert chosen is not None
            db.add(Matricula(
                aluno_id=chosen[0],
                curso_id=chosen[1],
                status_matricula='ativa',
                data_matricula=datetime.now(timezone.utc),
            ))
            db.commit()
        finally:
            db.close()

        updated = json.loads(await asyncio.wait_for(socket.recv(), timeout=7))
        assert updated['event'] == 'analytics.snapshot', updated
        assert updated['data']['kpis']['enrollments'] == before + 1, (before, updated['data']['kpis'])


asyncio.run(main())
PY

printf '%s\n' 'Advanced Analytics HTTPS/WSS smoke passed.'
