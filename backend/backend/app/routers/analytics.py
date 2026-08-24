from __future__ import annotations

import asyncio
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import SessionLocal, get_db
from app.realtime import authenticate_realtime_token
from app.services.analytics_service import (
    AnalyticsFilters,
    build_dashboard,
    dashboard_fingerprint,
    dashboard_to_csv,
    dashboard_to_pdf,
    filters_from_payload,
    resolve_filters,
)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])
ws_router = APIRouter(tags=["Advanced Analytics"])
AUTH_TIMEOUT_SECONDS = 8
SNAPSHOT_INTERVAL_SECONDS = 2


def _rest_filters(
    start_date: date | None,
    end_date: date | None,
    category_id: int | None,
    enrollment_status: str | None,
) -> AnalyticsFilters:
    try:
        return resolve_filters(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            enrollment_status=enrollment_status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/dashboard")
def dashboard(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category_id: int | None = Query(default=None),
    enrollment_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles("admin")),
):
    del identity
    filters = _rest_filters(start_date, end_date, category_id, enrollment_status)
    try:
        snapshot = build_dashboard(db, filters)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return success_response(data=snapshot, message="Analytics retornado com sucesso.")


@router.get("/export.csv")
def export_csv(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category_id: int | None = Query(default=None),
    enrollment_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles("admin")),
):
    del identity
    filters = _rest_filters(start_date, end_date, category_id, enrollment_status)
    try:
        snapshot = build_dashboard(db, filters)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return Response(
        content=dashboard_to_csv(snapshot),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=analytics.csv"},
    )


@router.get("/export.pdf")
def export_pdf(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    category_id: int | None = Query(default=None),
    enrollment_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    identity=Depends(allowed_roles("admin")),
):
    del identity
    filters = _rest_filters(start_date, end_date, category_id, enrollment_status)
    try:
        snapshot = build_dashboard(db, filters)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return Response(
        content=dashboard_to_pdf(snapshot),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analytics.pdf"},
    )


def _snapshot_for_ws(filters: AnalyticsFilters) -> dict[str, object]:
    db = SessionLocal()
    try:
        return build_dashboard(db, filters)
    finally:
        db.close()


@ws_router.websocket("/ws/analytics")
async def analytics_realtime(websocket: WebSocket) -> None:
    """Admin-only realtime analytics snapshots over the authenticated WS layer."""

    await websocket.accept()
    try:
        try:
            auth_frame = await asyncio.wait_for(websocket.receive_json(), timeout=AUTH_TIMEOUT_SECONDS)
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
        if identity["role"] != "admin":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.send_json({"event": "analytics.ready", "user_id": identity["id"]})
        filters = resolve_filters()
        subscribed = False
        previous_fingerprint: str | None = None

        while True:
            frame = None
            try:
                frame = await asyncio.wait_for(
                    websocket.receive_json(), timeout=SNAPSHOT_INTERVAL_SECONDS
                )
            except asyncio.TimeoutError:
                pass

            if frame is not None:
                if not isinstance(frame, dict):
                    continue
                frame_type = frame.get("type")
                if frame_type == "analytics.subscribe":
                    try:
                        filters = filters_from_payload(frame.get("filters", {}))
                        # Validate referenced category before acknowledging the subscription.
                        snapshot = await asyncio.to_thread(_snapshot_for_ws, filters)
                    except ValueError as exc:
                        await websocket.send_json({"event": "analytics.error", "message": str(exc)})
                        continue
                    subscribed = True
                    previous_fingerprint = dashboard_fingerprint(snapshot)
                    await websocket.send_json(
                        {"event": "analytics.snapshot", "data": jsonable_encoder(snapshot)}
                    )
                    continue
                if frame_type == "ping":
                    await websocket.send_json({"event": "analytics.pong"})
                    continue
                if frame_type == "close":
                    await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                    return

            if not subscribed:
                continue
            try:
                snapshot = await asyncio.to_thread(_snapshot_for_ws, filters)
            except ValueError as exc:
                await websocket.send_json({"event": "analytics.error", "message": str(exc)})
                continue
            fingerprint = dashboard_fingerprint(snapshot)
            if fingerprint != previous_fingerprint:
                previous_fingerprint = fingerprint
                await websocket.send_json(
                    {"event": "analytics.snapshot", "data": jsonable_encoder(snapshot)}
                )
    except WebSocketDisconnect:
        return
    except (ValueError, TypeError):
        try:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
        except RuntimeError:
            pass
