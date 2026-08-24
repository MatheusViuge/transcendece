from app.database import SessionLocal
from app.models.chat import ChatMessage, Conversation
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


def _user_id(client, headers: dict[str, str]) -> int:
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    return response.json()["data"]["id"]


def test_direct_conversation_is_canonical_and_private(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    bernardo = _login(client, "bernardo.lima@seed.example.com")
    alice_id = _user_id(client, alice)
    camila_id = _user_id(client, camila)

    created = client.post("/chat/conversations", headers=alice, json={"recipient_id": camila_id})
    assert created.status_code == 201, created.text
    conversation_id = created.json()["data"]["id"]
    assert created.json()["data"]["participant"]["id"] == camila_id

    inverse = client.post("/chat/conversations", headers=camila, json={"recipient_id": alice_id})
    assert inverse.status_code == 200
    assert inverse.json()["data"]["id"] == conversation_id

    assert client.post("/chat/conversations", headers=alice, json={"recipient_id": alice_id}).status_code == 422
    assert client.get(f"/chat/conversations/{conversation_id}/messages", headers=bernardo).status_code == 404
    assert client.post(
        f"/chat/conversations/{conversation_id}/messages",
        headers=bernardo,
        json={"content": "intrusão"},
    ).status_code == 404

    db = SessionLocal()
    try:
        row = db.query(Conversation).filter(Conversation.id == conversation_id).one()
        assert row.user_low_id == min(alice_id, camila_id)
        assert row.user_high_id == max(alice_id, camila_id)
        assert db.query(Conversation).count() == 1
    finally:
        db.close()


def test_messages_persist_and_cursor_pagination_is_stable(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    alice_id = _user_id(client, alice)
    camila_id = _user_id(client, camila)

    conversation_id = client.post(
        "/chat/conversations", headers=alice, json={"recipient_id": camila_id}
    ).json()["data"]["id"]

    payloads = [
        (alice, "Primeira mensagem"),
        (camila, "Segunda mensagem"),
        (alice, "Terceira mensagem"),
    ]
    sent_ids = []
    for headers, content in payloads:
        response = client.post(
            f"/chat/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": content},
        )
        assert response.status_code == 201, response.text
        assert response.json()["data"]["event"] == "chat.message.created"
        sent_ids.append(response.json()["data"]["id"])

    page = client.get(
        f"/chat/conversations/{conversation_id}/messages",
        headers=camila,
        params={"limit": 2},
    )
    assert page.status_code == 200
    data = page.json()["data"]
    assert [item["content"] for item in data["items"]] == ["Segunda mensagem", "Terceira mensagem"]
    assert data["has_more"] is True
    assert data["next_before_id"] == sent_ids[1]

    older = client.get(
        f"/chat/conversations/{conversation_id}/messages",
        headers=camila,
        params={"limit": 2, "before_id": data["next_before_id"]},
    )
    assert [item["content"] for item in older.json()["data"]["items"]] == ["Primeira mensagem"]
    assert older.json()["data"]["has_more"] is False

    listed = client.get("/chat/conversations", headers=alice)
    assert listed.status_code == 200
    conversation = next(item for item in listed.json()["data"]["items"] if item["id"] == conversation_id)
    assert conversation["participant"]["id"] == camila_id
    assert conversation["last_message"]["content"] == "Terceira mensagem"

    db = SessionLocal()
    try:
        assert db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).count() == 3
        assert db.query(ChatMessage).filter(ChatMessage.sender_id == alice_id).count() == 2
    finally:
        db.close()


def test_message_validation_rejects_empty_and_oversized_content(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    camila_id = _user_id(client, camila)
    conversation_id = client.post(
        "/chat/conversations", headers=alice, json={"recipient_id": camila_id}
    ).json()["data"]["id"]

    assert client.post(
        f"/chat/conversations/{conversation_id}/messages",
        headers=alice,
        json={"content": "   "},
    ).status_code == 422
    assert client.post(
        f"/chat/conversations/{conversation_id}/messages",
        headers=alice,
        json={"content": "x" * 2001},
    ).status_code == 422
