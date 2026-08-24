from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from fastapi import HTTPException, WebSocket
from fastapi.encoders import jsonable_encoder

from app.core.security import ALLOWED_ROLES, verify_token
from app.database import SessionLocal
from app.models.user import Usuario


class RealtimeHub:
    """In-memory realtime connection registry for the single backend process.

    PostgreSQL remains the source of truth. The hub only fans out transient
    events to authenticated sockets connected to this process.
    """

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def register(self, user_id: int, websocket: WebSocket) -> None:
        self._connections[user_id].add(websocket)

    def unregister(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(user_id, None)

    async def publish_to_users(self, user_ids: Iterable[int], payload: dict[str, object]) -> None:
        encoded = jsonable_encoder(payload)
        stale: list[tuple[int, WebSocket]] = []
        for user_id in set(user_ids):
            for websocket in tuple(self._connections.get(user_id, ())):
                try:
                    await websocket.send_json(encoded)
                except Exception:
                    stale.append((user_id, websocket))
        for user_id, websocket in stale:
            self.unregister(user_id, websocket)

    def connection_count(self, user_id: int) -> int:
        return len(self._connections.get(user_id, ()))


realtime_hub = RealtimeHub()


def authenticate_realtime_token(token: str) -> dict[str, object]:
    """Resolve a WebSocket identity using the same JWT and DB rules as REST."""

    try:
        identity = verify_token(token)
    except HTTPException as exc:
        raise ValueError("invalid token") from exc

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id == identity["id"]).first()
        if user is None or user.email.strip().lower() != identity["email"]:
            raise ValueError("invalid session")
        if not getattr(user, "is_active", True):
            raise ValueError("inactive account")
        if user.tipo_usuario not in ALLOWED_ROLES:
            raise ValueError("invalid role")
        return {
            "id": user.id,
            "email": user.email,
            "role": user.tipo_usuario,
        }
    finally:
        db.close()
