from app.core.api_key_auth import PUBLIC_API_RATE_LIMIT
from app.database import SessionLocal
from app.models.api_key import ApiKey
from scripts.seed_advanced_search import SEED_PASSWORD, populate

ANA = "ana.ribeiro@seed.example.com"
BRUNO = "bruno.costa@seed.example.com"
KEYS_PATH = "/keys"


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "senha": SEED_PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def _create_key(client, token: str, *, name: str, scopes: list[str]) -> dict:
    response = client.post(
        KEYS_PATH,
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "scopes": scopes},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


def _api_headers(secret: str) -> dict[str, str]:
    return {"X-API-Key": secret}


def test_api_key_lifecycle_never_persists_or_reveals_plain_secret(client):
    _seed()
    token = _login(client, ANA)
    created = _create_key(
        client,
        token,
        name="integration",
        scopes=["courses:read", "courses:write"],
    )
    secret = created["secret"]
    assert secret.startswith(created["prefix"] + "_")

    db = SessionLocal()
    try:
        persisted = db.query(ApiKey).filter(ApiKey.id == created["id"]).one()
        assert persisted.key_hash != secret
        assert secret not in persisted.key_hash
        assert len(persisted.key_hash) == 64
    finally:
        db.close()

    listed = client.get(KEYS_PATH, headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert "secret" not in listed.text
    assert "key_hash" not in listed.text

    working = client.get("/v1/public/courses", headers=_api_headers(secret))
    assert working.status_code == 200
    assert working.headers["X-RateLimit-Limit"] == str(PUBLIC_API_RATE_LIMIT)

    rotated = client.post(
        f"{KEYS_PATH}/{created['id']}/rotate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rotated.status_code == 201, rotated.text
    replacement = rotated.json()["data"]
    assert replacement["secret"] != secret
    assert client.get("/v1/public/courses", headers=_api_headers(secret)).status_code == 401
    assert client.get(
        "/v1/public/courses",
        headers=_api_headers(replacement["secret"]),
    ).status_code == 200

    revoked = client.delete(
        f"{KEYS_PATH}/{replacement['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoked.status_code == 200
    assert revoked.json()["data"]["active"] is False
    assert client.get(
        "/v1/public/courses",
        headers=_api_headers(replacement["secret"]),
    ).status_code == 401


def test_public_api_requires_key_and_enforces_scopes_and_course_ownership(client):
    _seed()

    assert client.get("/v1/public/courses").status_code == 401
    assert client.get("/v1/public/courses", headers={"X-API-Key": "invalid"}).status_code == 401

    ana_token = _login(client, ANA)
    ana_key = _create_key(
        client,
        ana_token,
        name="ana-write",
        scopes=["courses:read", "courses:write"],
    )
    read_only = _create_key(
        client,
        ana_token,
        name="ana-read",
        scopes=["courses:read"],
    )

    listing = client.get(
        "/v1/public/courses?page=1&page_size=5",
        headers=_api_headers(ana_key["secret"]),
    )
    assert listing.status_code == 200, listing.text
    page = listing.json()["data"]
    assert page["pagination"]["page_size"] == 5
    assert len(page["items"]) == 5
    first = page["items"][0]

    detail = client.get(
        f"/v1/public/courses/{first['id']}",
        headers=_api_headers(ana_key["secret"]),
    )
    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == first["id"]

    payload = {
        "title": "Public API Integration Course",
        "description": "Curso criado exclusivamente pelo teste da Public API.",
        "price": 42.0,
        "workload_hours": 8,
        "category_id": first["category"]["id"],
        "level_id": first["level"]["id"],
    }

    forbidden = client.post(
        "/v1/public/courses",
        headers=_api_headers(read_only["secret"]),
        json=payload,
    )
    assert forbidden.status_code == 403

    created = client.post(
        "/v1/public/courses",
        headers=_api_headers(ana_key["secret"]),
        json=payload,
    )
    assert created.status_code == 201, created.text
    course_id = created.json()["data"]["id"]
    assert created.json()["data"]["instructor"]["name"] == "Ana Ribeiro"

    updated = client.put(
        f"/v1/public/courses/{course_id}",
        headers=_api_headers(ana_key["secret"]),
        json={"title": "Public API Integration Course Updated", "price": 84.0},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["title"].endswith("Updated")
    assert updated.json()["data"]["price"] == 84.0

    bruno_token = _login(client, BRUNO)
    bruno_key = _create_key(
        client,
        bruno_token,
        name="bruno-write",
        scopes=["courses:read", "courses:write"],
    )
    assert client.put(
        f"/v1/public/courses/{course_id}",
        headers=_api_headers(bruno_key["secret"]),
        json={"title": "Tentativa indevida"},
    ).status_code == 404
    assert client.delete(
        f"/v1/public/courses/{course_id}",
        headers=_api_headers(bruno_key["secret"]),
    ).status_code == 404

    deleted = client.delete(
        f"/v1/public/courses/{course_id}",
        headers=_api_headers(ana_key["secret"]),
    )
    assert deleted.status_code == 204
    assert client.get(
        f"/v1/public/courses/{course_id}",
        headers=_api_headers(ana_key["secret"]),
    ).status_code == 404


def test_non_instructor_cannot_issue_write_key_and_invalid_payload_is_rejected(client):
    _seed()
    student_token = _login(client, "alice.ferreira@seed.example.com")
    forbidden = client.post(
        KEYS_PATH,
        headers={"Authorization": f"Bearer {student_token}"},
        json={"name": "student-write", "scopes": ["courses:read", "courses:write"]},
    )
    assert forbidden.status_code == 403

    ana_token = _login(client, ANA)
    ana_key = _create_key(
        client,
        ana_token,
        name="validation",
        scopes=["courses:read", "courses:write"],
    )
    invalid = client.post(
        "/v1/public/courses",
        headers=_api_headers(ana_key["secret"]),
        json={
            "title": "",
            "description": "",
            "price": -1,
            "workload_hours": 0,
            "category_id": 0,
            "level_id": 0,
        },
    )
    assert invalid.status_code == 422


def test_rate_limit_is_per_api_key_and_returns_429(client):
    _seed()
    token = _login(client, ANA)
    limited = _create_key(client, token, name="limited", scopes=["courses:read"])
    independent = _create_key(client, token, name="independent", scopes=["courses:read"])

    for _ in range(PUBLIC_API_RATE_LIMIT):
        response = client.get("/v1/public/courses?page_size=1", headers=_api_headers(limited["secret"]))
        assert response.status_code == 200, response.text

    blocked = client.get("/v1/public/courses?page_size=1", headers=_api_headers(limited["secret"]))
    assert blocked.status_code == 429
    assert blocked.headers["X-RateLimit-Remaining"] == "0"
    assert int(blocked.headers["Retry-After"]) >= 1

    other_key = client.get(
        "/v1/public/courses?page_size=1",
        headers=_api_headers(independent["secret"]),
    )
    assert other_key.status_code == 200
