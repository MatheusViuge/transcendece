import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.database import SessionLocal
from scripts.seed_advanced_search import SEED_PASSWORD, populate


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client: TestClient, email: str) -> tuple[str, dict[str, str]]:
    response = client.post("/auth/login", json={"email": email, "senha": SEED_PASSWORD})
    assert response.status_code == 200, response.text
    token = response.json()["data"]["access_token"]
    return token, {"Authorization": f"Bearer {token}"}


def _user_id(client: TestClient, headers: dict[str, str]) -> int:
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]["id"]


def _authenticate_socket(socket, token: str) -> dict:
    socket.send_json({"type": "auth", "token": token})
    ready = socket.receive_json()
    assert ready["event"] == "realtime.ready"
    return ready


def test_websocket_broadcast_is_authenticated_and_scoped(client: TestClient):
    _seed()
    alice_token, alice = _login(client, "alice.ferreira@seed.example.com")
    camila_token, camila = _login(client, "camila.nunes@seed.example.com")
    bernardo_token, _ = _login(client, "bernardo.lima@seed.example.com")
    camila_id = _user_id(client, camila)

    created = client.post("/chat/conversations", headers=alice, json={"recipient_id": camila_id})
    assert created.status_code == 201, created.text
    conversation_id = created.json()["data"]["id"]

    with client.websocket_connect("/ws/chat") as alice_ws, client.websocket_connect("/ws/chat") as camila_ws, client.websocket_connect("/ws/chat") as bernardo_ws:
        _authenticate_socket(alice_ws, alice_token)
        _authenticate_socket(camila_ws, camila_token)
        _authenticate_socket(bernardo_ws, bernardo_token)

        sent = client.post(
            f"/chat/conversations/{conversation_id}/messages",
            headers=alice,
            json={"content": "Mensagem realtime"},
        )
        assert sent.status_code == 201, sent.text
        message_id = sent.json()["data"]["id"]

        alice_event = alice_ws.receive_json()
        camila_event = camila_ws.receive_json()
        assert alice_event["event"] == "chat.message.created"
        assert camila_event["event"] == "chat.message.created"
        assert alice_event["id"] == message_id
        assert camila_event["id"] == message_id
        assert alice_event["conversation_id"] == conversation_id

        # A third authenticated user must not receive another conversation's event.
        # Sending ping gives us a deterministic next frame: a leaked chat event would
        # arrive before pong and make this assertion fail.
        bernardo_ws.send_json({"type": "ping"})
        assert bernardo_ws.receive_json() == {"event": "realtime.pong"}


def test_websocket_rejects_invalid_authentication(client: TestClient):
    with client.websocket_connect("/ws/chat") as socket:
        socket.send_json({"type": "auth", "token": "invalid-token"})
        with pytest.raises(WebSocketDisconnect) as exc_info:
            socket.receive_json()
        assert exc_info.value.code == 1008


def test_reconnect_gap_can_be_recovered_with_after_id(client: TestClient):
    _seed()
    alice_token, alice = _login(client, "alice.ferreira@seed.example.com")
    camila_token, camila = _login(client, "camila.nunes@seed.example.com")
    camila_id = _user_id(client, camila)

    created = client.post("/chat/conversations", headers=alice, json={"recipient_id": camila_id})
    conversation_id = created.json()["data"]["id"]

    with client.websocket_connect("/ws/chat") as alice_ws, client.websocket_connect("/ws/chat") as camila_ws:
        _authenticate_socket(alice_ws, alice_token)
        _authenticate_socket(camila_ws, camila_token)
        first = client.post(
            f"/chat/conversations/{conversation_id}/messages",
            headers=alice,
            json={"content": "Antes da queda"},
        )
        first_id = first.json()["data"]["id"]
        assert alice_ws.receive_json()["id"] == first_id
        assert camila_ws.receive_json()["id"] == first_id

    # Both sockets are disconnected here. Persist messages while Camila is offline.
    second = client.post(
        f"/chat/conversations/{conversation_id}/messages",
        headers=alice,
        json={"content": "Durante a queda 1"},
    )
    third = client.post(
        f"/chat/conversations/{conversation_id}/messages",
        headers=alice,
        json={"content": "Durante a queda 2"},
    )
    assert second.status_code == 201
    assert third.status_code == 201

    with client.websocket_connect("/ws/chat") as camila_ws:
        _authenticate_socket(camila_ws, camila_token)
        recovered = client.get(
            f"/chat/conversations/{conversation_id}/messages",
            headers=camila,
            params={"after_id": first_id, "limit": 100},
        )
        assert recovered.status_code == 200, recovered.text
        page = recovered.json()["data"]
        assert [item["content"] for item in page["items"]] == [
            "Durante a queda 1",
            "Durante a queda 2",
        ]
        assert page["has_more"] is False
        assert page["next_after_id"] is None


def test_message_cursor_rejects_before_and_after_together(client: TestClient):
    _seed()
    _, alice = _login(client, "alice.ferreira@seed.example.com")
    _, camila = _login(client, "camila.nunes@seed.example.com")
    camila_id = _user_id(client, camila)
    conversation_id = client.post(
        "/chat/conversations", headers=alice, json={"recipient_id": camila_id}
    ).json()["data"]["id"]

    response = client.get(
        f"/chat/conversations/{conversation_id}/messages",
        headers=alice,
        params={"before_id": 10, "after_id": 1},
    )
    assert response.status_code == 422
