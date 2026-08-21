from app.database import SessionLocal
from app.main import create_app
from app.models.user import Usuario


VALID_USER = {
    "nome": "Framework",
    "sobrenome": "Reviewer",
    "email": "framework-reviewer@example.com",
    "senha_hash": "Framework#123",
    "data_nascimento": "2000-01-01",
}


def _promote_to_admin(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.email == email).one()
        user.tipo_usuario = "admin"
        db.commit()
    finally:
        db.close()


def _admin_headers(client) -> dict[str, str]:
    register = client.post("/auth/register", json=VALID_USER)
    assert register.status_code == 201

    _promote_to_admin(VALID_USER["email"])

    login = client.post(
        "/auth/login",
        json={"email": VALID_USER["email"], "senha": VALID_USER["senha_hash"]},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_application_factory_exposes_framework_routes():
    paths = set(create_app().openapi()["paths"])

    assert "/status" in paths
    assert "/auth/register" in paths
    assert "/auth/login" in paths
    assert "/categories/" in paths
    assert "/courses/" in paths
    assert "/enrollments/" in paths


def test_fastapi_service_repository_orm_crud_flow(client):
    """Exercise FastAPI -> service -> repository -> SQLAlchemy through HTTP."""
    headers = _admin_headers(client)

    create = client.post(
        "/categories/",
        headers=headers,
        json={"nome": "Frameworks", "descricao": "Categoria de integração."},
    )
    assert create.status_code == 201
    category_id = create.json()["data"]["id"]

    list_response = client.get("/categories/")
    assert list_response.status_code == 200
    assert any(item["id"] == category_id for item in list_response.json()["data"])

    update = client.patch(
        f"/categories/{category_id}",
        headers=headers,
        json={"descricao": "Atualizada pelo fluxo HTTP completo."},
    )
    assert update.status_code == 200
    assert update.json()["data"]["descricao"] == "Atualizada pelo fluxo HTTP completo."

    delete = client.delete(f"/categories/{category_id}", headers=headers)
    assert delete.status_code == 200
    assert delete.json()["data"] is None

    final_list = client.get("/categories/")
    assert final_list.status_code == 200
    assert all(item["id"] != category_id for item in final_list.json()["data"])
