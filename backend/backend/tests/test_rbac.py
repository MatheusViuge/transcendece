from app.database import SessionLocal
from app.models.course import Curso
from app.models.user import Usuario
from scripts.seed_advanced_search import SEED_PASSWORD
from scripts.seed_rbac import RBAC_ADMIN_EMAIL, populate


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client, email: str, password: str = SEED_PASSWORD) -> str:
    response = client.post("/auth/login", json={"email": email, "senha": password})
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_crud_roles_and_sensitive_fields_are_protected(client):
    _seed()
    admin_token = _login(client, RBAC_ADMIN_EMAIL)
    student_token = _login(client, "alice.ferreira@seed.example.com")

    denied = client.get("/admin/users", headers=_bearer(student_token))
    assert denied.status_code == 403

    listing = client.get("/admin/users?page=1&page_size=5&q=alice", headers=_bearer(admin_token))
    assert listing.status_code == 200, listing.text
    data = listing.json()["data"]
    assert data["pagination"]["total"] == 1
    assert data["items"][0]["email"] == "alice.ferreira@seed.example.com"
    assert "senha_hash" not in listing.text
    assert "password" not in listing.text.lower()

    created = client.post(
        "/admin/users",
        headers=_bearer(admin_token),
        json={
            "nome": "Teste",
            "sobrenome": "RBAC",
            "email": "teste.rbac@seed.example.com",
            "senha": "Rbac42!",
            "data_nascimento": "1999-01-01",
            "role": "aluno",
        },
    )
    assert created.status_code == 201, created.text
    user_id = created.json()["data"]["id"]

    updated = client.patch(
        f"/admin/users/{user_id}",
        headers=_bearer(admin_token),
        json={"nome": "Teste Atualizado"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["nome"] == "Teste Atualizado"

    specialties = client.get("/admin/specialties", headers=_bearer(admin_token))
    assert specialties.status_code == 200
    specialty_id = specialties.json()["data"][0]["id"]

    promoted = client.patch(
        f"/admin/users/{user_id}/role",
        headers=_bearer(admin_token),
        json={"role": "instrutor", "especialidade_id": specialty_id},
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["data"]["tipo_usuario"] == "instrutor"

    deactivated = client.delete(f"/admin/users/{user_id}", headers=_bearer(admin_token))
    assert deactivated.status_code == 200
    assert deactivated.json()["data"]["is_active"] is False

    assert client.post(
        "/auth/login",
        json={"email": "teste.rbac@seed.example.com", "senha": "Rbac42!"},
    ).status_code == 403


def test_role_changes_take_effect_without_reissuing_jwt_and_self_lockout_is_blocked(client):
    _seed()
    admin_token = _login(client, RBAC_ADMIN_EMAIL)
    alice_token = _login(client, "alice.ferreira@seed.example.com")

    db = SessionLocal()
    try:
        alice = db.query(Usuario).filter(Usuario.email == "alice.ferreira@seed.example.com").one()
        alice_id = alice.id
        admin = db.query(Usuario).filter(Usuario.email == RBAC_ADMIN_EMAIL).one()
        admin_id = admin.id
    finally:
        db.close()

    assert client.get("/admin/users", headers=_bearer(alice_token)).status_code == 403

    promoted = client.patch(
        f"/admin/users/{alice_id}/role",
        headers=_bearer(admin_token),
        json={"role": "admin"},
    )
    assert promoted.status_code == 200
    assert client.get("/admin/users", headers=_bearer(alice_token)).status_code == 200

    demoted = client.patch(
        f"/admin/users/{alice_id}/role",
        headers=_bearer(admin_token),
        json={"role": "aluno"},
    )
    assert demoted.status_code == 200
    assert client.get("/admin/users", headers=_bearer(alice_token)).status_code == 403

    assert client.patch(
        f"/admin/users/{admin_id}/role",
        headers=_bearer(admin_token),
        json={"role": "aluno"},
    ).status_code == 409
    assert client.delete(f"/admin/users/{admin_id}", headers=_bearer(admin_token)).status_code == 409


def test_instructor_cannot_read_another_instructors_statistics_by_id(client):
    _seed()
    ana_token = _login(client, "ana.ribeiro@seed.example.com")
    bruno_token = _login(client, "bruno.costa@seed.example.com")

    db = SessionLocal()
    try:
        ana = db.query(Usuario).filter(Usuario.email == "ana.ribeiro@seed.example.com").one()
        ana_course = db.query(Curso).filter(Curso.instrutor_id == ana.id).first()
        assert ana_course is not None
        course_id = ana_course.id
    finally:
        db.close()

    own = client.get(f"/courses/{course_id}/statistics", headers=_bearer(ana_token))
    assert own.status_code == 200, own.text

    forbidden = client.get(f"/courses/{course_id}/statistics", headers=_bearer(bruno_token))
    assert forbidden.status_code == 403


def test_inactive_account_invalidates_existing_session_immediately(client):
    _seed()
    admin_token = _login(client, RBAC_ADMIN_EMAIL)
    student_email = "camila.nunes@seed.example.com"
    student_token = _login(client, student_email)

    db = SessionLocal()
    try:
        student_id = db.query(Usuario).filter(Usuario.email == student_email).one().id
    finally:
        db.close()

    assert client.get("/auth/me", headers=_bearer(student_token)).status_code == 200
    disabled = client.patch(
        f"/admin/users/{student_id}/status",
        headers=_bearer(admin_token),
        json={"is_active": False},
    )
    assert disabled.status_code == 200
    assert client.get("/auth/me", headers=_bearer(student_token)).status_code == 403


def test_inactive_owner_invalidates_existing_public_api_key(client):
    _seed()
    admin_token = _login(client, RBAC_ADMIN_EMAIL)
    ana_token = _login(client, "ana.ribeiro@seed.example.com")

    created = client.post(
        "/keys",
        headers=_bearer(ana_token),
        json={"name": "rbac-owner-state", "scopes": ["courses:read", "courses:write"]},
    )
    assert created.status_code == 201, created.text
    secret = created.json()["data"]["secret"]
    headers = {"X-API-Key": secret}
    assert client.get("/v1/public/courses?page_size=1", headers=headers).status_code == 200

    db = SessionLocal()
    try:
        ana_id = db.query(Usuario).filter(Usuario.email == "ana.ribeiro@seed.example.com").one().id
    finally:
        db.close()

    disabled = client.patch(
        f"/admin/users/{ana_id}/status",
        headers=_bearer(admin_token),
        json={"is_active": False},
    )
    assert disabled.status_code == 200
    assert client.get("/v1/public/courses?page_size=1", headers=headers).status_code == 401
