from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.friendship import Friendship
from app.models.user import Usuario
from scripts.seed_advanced_search import SEED_PASSWORD, populate


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


def test_profile_update_and_public_privacy(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    own = client.get("/users/me", headers=alice)
    assert own.status_code == 200
    assert own.json()["data"]["avatar_url"] == "/default-avatar.svg"
    updated = client.patch("/users/me", headers=alice, json={"nome": "Alicia", "sobrenome": "Ferreira"})
    assert updated.status_code == 200
    assert updated.json()["data"]["nome"] == "Alicia"
    protected = client.patch("/users/me", headers=alice, json={"tipo_usuario": "admin", "is_active": False})
    assert protected.status_code == 422
    public = client.get(f"/users/{own.json()['data']['id']}", headers=camila)
    assert public.status_code == 200
    assert "email" not in public.json()["data"]
    assert "data_nascimento" not in public.json()["data"]


def test_friend_lifecycle_and_constraints(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]
    camila_id = client.get("/users/me", headers=camila).json()["data"]["id"]
    assert client.post(f"/users/friends/{alice_id}", headers=alice).status_code == 422
    assert client.post(f"/users/friends/{camila_id}", headers=alice).status_code == 201
    assert client.post(f"/users/friends/{camila_id}", headers=alice).status_code == 409
    assert [item["id"] for item in client.get("/users/friends", headers=alice).json()["data"]] == [camila_id]
    assert [item["id"] for item in client.get("/users/friends", headers=camila).json()["data"]] == [alice_id]
    db = SessionLocal()
    try:
        assert db.query(Friendship).count() == 1
    finally:
        db.close()
    assert client.delete(f"/users/friends/{camila_id}", headers=alice).status_code == 200
    assert client.get("/users/friends", headers=alice).json()["data"] == []


def test_presence_heartbeat_timeout_visible_to_friends(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]
    assert client.post(f"/users/friends/{alice_id}", headers=camila).status_code == 201
    assert client.post("/users/presence/heartbeat", headers=alice).status_code == 200
    entry = next(item for item in client.get("/users/friends", headers=camila).json()["data"] if item["id"] == alice_id)
    assert entry["online"] is True
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == alice_id).one()
        user.last_seen_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()
    entry = next(item for item in client.get("/users/friends", headers=camila).json()["data"] if item["id"] == alice_id)
    assert entry["online"] is False


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
