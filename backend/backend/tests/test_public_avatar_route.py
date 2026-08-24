from app.database import SessionLocal
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


def test_selected_avatar_is_renderable_without_authorization_header(client):
    """Regression: a browser <img src> request does not send the SPA Bearer token."""
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    alice_id = client.get("/users/me", headers=alice).json()["data"]["id"]

    default = client.get(f"/users/{alice_id}/avatar", follow_redirects=False)
    assert default.status_code == 307
    assert default.headers["location"] == "/default-avatar.svg"

    avatar_bytes = b"\x89PNG\r\n\x1a\npublic-avatar-regression"
    upload = client.post(
        "/files",
        headers=alice,
        data={"purpose": "avatar"},
        files={"file": ("avatar.png", avatar_bytes, "image/png")},
    )
    assert upload.status_code == 201, upload.text

    selected = client.put(f"/users/me/avatar/{upload.json()['data']['id']}", headers=alice)
    assert selected.status_code == 200, selected.text
    assert selected.json()["data"]["avatar_url"] == f"/api/users/{alice_id}/avatar"

    browser_like_request = client.get(f"/users/{alice_id}/avatar")
    assert browser_like_request.status_code == 200, browser_like_request.text
    assert browser_like_request.headers["content-type"].startswith("image/png")
    assert browser_like_request.content == avatar_bytes
