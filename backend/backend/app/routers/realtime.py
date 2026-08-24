from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.realtime import authenticate_realtime_token, realtime_hub

router = APIRouter(tags=["Realtime"])
AUTH_TIMEOUT_SECONDS = 8


@router.websocket("/ws/chat")
async def chat_realtime(websocket: WebSocket) -> None:
    """Authenticated chat event stream.

    The browser opens the socket first and immediately sends an auth frame:
    {"type": "auth", "token": "<JWT>"}. Keeping the bearer token out of the
    URL avoids leaking it through proxy access logs and browser history.
    """

    await websocket.accept()
    user_id: int | None = None

    try:
        try:
            auth_frame = await asyncio.wait_for(
                websocket.receive_json(), timeout=AUTH_TIMEOUT_SECONDS
            )
        except (asyncio.TimeoutError, ValueError, TypeError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if not isinstance(auth_frame, dict) or auth_frame.get("type") != "auth":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        token = auth_frame.get("token")
        if not isinstance(token, str) or not token.strip():
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            identity = authenticate_realtime_token(token.strip())
        except ValueError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = int(identity["id"])
        await realtime_hub.register(user_id, websocket)
        await websocket.send_json({"event": "realtime.ready", "user_id": user_id})

        while True:
            frame = await websocket.receive_json()
            if not isinstance(frame, dict):
                continue
            frame_type = frame.get("type")
            if frame_type == "ping":
                await websocket.send_json({"event": "realtime.pong"})
            elif frame_type == "close":
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                return
    except WebSocketDisconnect:
        pass
    except (ValueError, TypeError):
        try:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        except RuntimeError:
            pass
    finally:
        if user_id is not None:
            realtime_hub.unregister(user_id, websocket)
