from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.database import SessionLocal
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.user import Usuario
from scripts.seed_analytics import populate
from scripts.seed_rbac import RBAC_ADMIN_EMAIL, RBAC_ADMIN_PASSWORD
from scripts.seed_advanced_search import SEED_PASSWORD


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client: TestClient, email: str, password: str = SEED_PASSWORD) -> tuple[str, dict[str, str]]:
    response = client.post("/auth/login", json={"email": email, "senha": password})
    assert response.status_code == 200, response.text
    token = response.json()["data"]["access_token"]
    return token, {"Authorization": f"Bearer {token}"}


def test_dashboard_is_admin_only_and_uses_real_filtered_data(client: TestClient):
    _seed()
    _, admin = _login(client, RBAC_ADMIN_EMAIL, RBAC_ADMIN_PASSWORD)
    _, alice = _login(client, "alice.ferreira@seed.example.com")

    forbidden = client.get("/analytics/dashboard", headers=alice)
    assert forbidden.status_code == 403

    response = client.get("/analytics/dashboard", headers=admin)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["kpis"]["enrollments"] > 0
    assert data["kpis"]["chat_messages"] >= 6
    assert len(data["daily_activity"]) == 30
    assert data["top_courses"]
    assert data["enrollment_statuses"]
    assert data["filter_options"]["categories"]

    completed = client.get(
        "/analytics/dashboard",
        headers=admin,
        params={"enrollment_status": "concluida"},
    )
    assert completed.status_code == 200
    completed_data = completed.json()["data"]
    assert completed_data["kpis"]["enrollments"] > 0
    assert completed_data["kpis"]["completion_rate"] == 100.0
    assert {row["label"] for row in completed_data["enrollment_statuses"]} == {"concluida"}

    first_course_id = data["top_courses"][0]["course_id"]
    db = SessionLocal()
    try:
        category_id = db.query(Curso).filter(Curso.id == first_course_id).one().categoria_id
    finally:
        db.close()
    category_response = client.get(
        "/analytics/dashboard",
        headers=admin,
        params={"category_id": category_id},
    )
    assert category_response.status_code == 200
    category_data = category_response.json()["data"]
    assert category_data["filters"]["category_id"] == category_id
    assert category_data["kpis"]["enrollments"] <= data["kpis"]["enrollments"]


def test_date_range_validation_and_exports_use_selected_slice(client: TestClient):
    _seed()
    _, admin = _login(client, RBAC_ADMIN_EMAIL, RBAC_ADMIN_PASSWORD)
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=6)

    invalid = client.get(
        "/analytics/dashboard",
        headers=admin,
        params={"start_date": today.isoformat(), "end_date": start.isoformat()},
    )
    assert invalid.status_code == 422

    params = {
        "start_date": start.isoformat(),
        "end_date": today.isoformat(),
        "enrollment_status": "ativa",
    }
    dashboard = client.get("/analytics/dashboard", headers=admin, params=params)
    assert dashboard.status_code == 200
    assert len(dashboard.json()["data"]["daily_activity"]) == 7

    csv_response = client.get("/analytics/export.csv", headers=admin, params=params)
    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    csv_text = csv_response.content.decode("utf-8-sig")
    assert start.isoformat() in csv_text
    assert today.isoformat() in csv_text
    assert "ativa" in csv_text
    assert "daily_activity" in csv_text

    pdf_response = client.get("/analytics/export.pdf", headers=admin, params=params)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF-1.4")
    assert start.isoformat().encode() in pdf_response.content
    assert today.isoformat().encode() in pdf_response.content


def test_analytics_websocket_is_admin_only_and_pushes_database_changes(client: TestClient):
    _seed()
    admin_token, admin_headers = _login(client, RBAC_ADMIN_EMAIL, RBAC_ADMIN_PASSWORD)
    alice_token, _ = _login(client, "alice.ferreira@seed.example.com")

    with client.websocket_connect("/ws/analytics") as denied:
        denied.send_json({"type": "auth", "token": alice_token})
        with pytest.raises(WebSocketDisconnect) as exc_info:
            denied.receive_json()
        assert exc_info.value.code == 1008

    baseline = client.get("/analytics/dashboard", headers=admin_headers).json()["data"]
    baseline_enrollments = baseline["kpis"]["enrollments"]

    with client.websocket_connect("/ws/analytics") as socket:
        socket.send_json({"type": "auth", "token": admin_token})
        ready = socket.receive_json()
        assert ready["event"] == "analytics.ready"
        socket.send_json({"type": "analytics.subscribe", "filters": {}})
        initial = socket.receive_json()
        assert initial["event"] == "analytics.snapshot"
        assert initial["data"]["kpis"]["enrollments"] == baseline_enrollments

        db = SessionLocal()
        try:
            students = db.query(Usuario).filter(Usuario.tipo_usuario == "aluno").all()
            courses = db.query(Curso).all()
            pair = None
            for student in students:
                for course in courses:
                    exists = db.query(Matricula).filter(
                        Matricula.aluno_id == student.id,
                        Matricula.curso_id == course.id,
                    ).first()
                    if exists is None:
                        pair = (student, course)
                        break
                if pair is not None:
                    break
            assert pair is not None
            student, course = pair
            db.add(
                Matricula(
                    aluno_id=student.id,
                    curso_id=course.id,
                    status_matricula="ativa",
                    data_matricula=datetime.now(timezone.utc),
                )
            )
            db.commit()
        finally:
            db.close()

        updated = socket.receive_json()
        assert updated["event"] == "analytics.snapshot"
        assert updated["data"]["kpis"]["enrollments"] == baseline_enrollments + 1
