import re
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.friendship import FriendRequest, Friendship
from app.models.user import Usuario
from scripts.seed_advanced_search import SEED_PASSWORD, populate

FRIEND_CODE_RE = re.compile(r"^[A-Z2-9]{5}-[A-Z2-9]{5}$")


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client, email: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "senha": SEED_PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_profile_update_public_privacy_and_friend_code(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    own = client.get("/users/me", headers=alice)
    assert own.status_code == 200
    assert own.json()["data"]["avatar_url"] == "/default-avatar.svg"
    assert FRIEND_CODE_RE.fullmatch(own.json()["data"]["friend_code"])
    updated = client.patch("/users/me", headers=alice, json={"nome": "Alicia", "sobrenome": "Ferreira"})
    assert updated.status_code == 200
    assert updated.json()["data"]["nome"] == "Alicia"
    protected = client.patch("/users/me", headers=alice, json={"tipo_usuario": "admin", "is_active": False})
    assert protected.status_code == 422
    public = client.get(f"/users/{own.json()['data']['id']}", headers=camila)
    assert public.status_code == 200
    assert "email" not in public.json()["data"]
    assert "data_nascimento" not in public.json()["data"]
    assert public.json()["data"]["online"] is None
    assert public.json()["data"]["friend_code"] == own.json()["data"]["friend_code"]


def test_friend_request_lifecycle_requires_consent(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]
    camila_id = client.get("/users/me", headers=camila).json()["data"]["id"]

    assert client.post(f"/users/friend-requests/{alice_id}", headers=alice).status_code == 422
    sent = client.post(f"/users/friend-requests/{camila_id}", headers=alice)
    assert sent.status_code == 201, sent.text
    assert sent.json()["data"]["direction"] == "outgoing"

    assert client.get("/users/friends", headers=alice).json()["data"] == []
    assert client.get("/users/friends", headers=camila).json()["data"] == []
    assert client.post(f"/users/friend-requests/{camila_id}", headers=alice).status_code == 409
    assert client.post(f"/users/friend-requests/{alice_id}", headers=camila).status_code == 409
    assert client.post(f"/users/friends/{camila_id}", headers=alice).status_code == 405

    alice_requests = client.get("/users/friend-requests", headers=alice).json()["data"]
    camila_requests = client.get("/users/friend-requests", headers=camila).json()["data"]
    assert [item["user"]["id"] for item in alice_requests["outgoing"]] == [camila_id]
    assert [item["user"]["id"] for item in camila_requests["incoming"]] == [alice_id]
    assert camila_requests["incoming"][0]["user"]["online"] is None

    accepted = client.post(f"/users/friend-requests/{alice_id}/accept", headers=camila)
    assert accepted.status_code == 201, accepted.text
    assert [item["id"] for item in client.get("/users/friends", headers=alice).json()["data"]] == [camila_id]
    assert [item["id"] for item in client.get("/users/friends", headers=camila).json()["data"]] == [alice_id]
    assert client.get("/users/friend-requests", headers=alice).json()["data"] == {"incoming": [], "outgoing": []}

    db = SessionLocal()
    try:
        assert db.query(Friendship).count() == 1
        assert db.query(FriendRequest).count() == 0
    finally:
        db.close()

    assert client.delete(f"/users/friends/{camila_id}", headers=alice).status_code == 200
    assert client.get("/users/friends", headers=alice).json()["data"] == []
    assert client.get("/users/friends", headers=camila).json()["data"] == []


def test_friend_request_can_be_declined_or_cancelled(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]
    camila_id = client.get("/users/me", headers=camila).json()["data"]["id"]

    assert client.post(f"/users/friend-requests/{camila_id}", headers=alice).status_code == 201
    declined = client.delete(f"/users/friend-requests/{alice_id}", headers=camila)
    assert declined.status_code == 200
    assert "recusada" in declined.json()["message"].lower()
    assert client.get("/users/friends", headers=alice).json()["data"] == []

    assert client.post(f"/users/friend-requests/{camila_id}", headers=alice).status_code == 201
    cancelled = client.delete(f"/users/friend-requests/{camila_id}", headers=alice)
    assert cancelled.status_code == 200
    assert "cancelada" in cancelled.json()["message"].lower()


def test_presence_hidden_until_friendship_is_accepted(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_profile = client.get("/users/me", headers=alice).json()["data"]
    camila_profile = client.get("/users/me", headers=camila).json()["data"]
    alice_id = alice_profile["id"]
    camila_id = camila_profile["id"]
    alice_code = alice_profile["friend_code"]

    assert client.post("/users/presence/heartbeat", headers=alice).status_code == 200
    public = client.get(f"/users/{alice_id}", headers=camila).json()["data"]
    assert public["online"] is None

    search = client.get("/users", headers=camila, params={"q": alice_code.replace("-", "")})
    assert search.status_code == 200
    assert [item["id"] for item in search.json()["data"]] == [alice_id]
    assert search.json()["data"][0]["online"] is None
    assert "email" not in search.json()["data"][0]

    assert client.post(f"/users/friend-requests/{alice_id}", headers=camila).status_code == 201
    assert client.post(f"/users/friend-requests/{camila_id}/accept", headers=alice).status_code == 201

    friend_view = client.get(f"/users/{alice_id}", headers=camila).json()["data"]
    assert friend_view["online"] is True

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == alice_id).one()
        user.last_seen_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()
    friend_view = client.get(f"/users/{alice_id}", headers=camila).json()["data"]
    assert friend_view["online"] is False


def test_friend_codes_are_unique_for_seeded_users(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    own = client.get("/users/me", headers=alice).json()["data"]
    assert FRIEND_CODE_RE.fullmatch(own["friend_code"])
    db = SessionLocal()
    try:
        codes = [row.friend_code for row in db.query(Usuario).all()]
        assert all(code and FRIEND_CODE_RE.fullmatch(code) for code in codes)
        assert len(codes) == len(set(codes))
    finally:
        db.close()


def test_avatar_custom_default_and_cross_user_access(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]
    default = client.get(f"/users/{alice_id}/avatar", headers=camila, follow_redirects=False)
    assert default.status_code == 307
    assert default.headers["location"] == "/default-avatar.svg"
    upload = client.post("/files", headers=alice, data={"purpose": "avatar"}, files={"file": ("avatar.png", b"\x89PNG\r\n\x1a\nuser-avatar", "image/png")})
    assert upload.status_code == 201, upload.text
    file_id = upload.json()["data"]["id"]
    selected = client.put(f"/users/me/avatar/{file_id}", headers=alice)
    assert selected.status_code == 200
    assert selected.json()["data"]["avatar_url"] == f"/api/users/{alice_id}/avatar"
    public_avatar = client.get(f"/users/{alice_id}/avatar", headers=camila)
    assert public_avatar.status_code == 200
    assert public_avatar.content.startswith(b"\x89PNG")
    removed = client.delete("/users/me/avatar", headers=alice)
    assert removed.status_code == 200
    assert removed.json()["data"]["avatar_url"] == "/default-avatar.svg"
