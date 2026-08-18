VALID_USER = {
    "nome": "Test",
    "sobrenome": "Student",
    "email": "student@example.com",
    "senha_hash": "SenhaForte#123",
    "data_nascimento": "2000-01-01",
}


def register_user(client, **overrides):
    payload = {**VALID_USER, **overrides}
    return client.post("/auth/register", json=payload)


def login_user(client, email="student@example.com", password="SenhaForte#123"):
    return client.post("/auth/login", json={"email": email, "senha": password})


def test_signup_login_and_me_flow(client):
    register = register_user(client)
    assert register.status_code == 201
    register_json = register.json()
    assert register_json["data"]["email"] == "student@example.com"
    assert register_json["data"]["tipo_usuario"] == "aluno"
    assert "senha_hash" not in register_json["data"]
    assert "SenhaForte#123" not in register.text

    login = login_user(client)
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    assert token

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "student@example.com"


def test_duplicate_email_is_rejected(client):
    assert register_user(client).status_code == 201
    duplicate = register_user(client, email="STUDENT@example.com")

    assert duplicate.status_code == 400
    assert "senha" not in duplicate.text.lower()


def test_invalid_login_uses_generic_error(client):
    assert register_user(client).status_code == 201

    wrong_password = login_user(client, password="SenhaErrada#123")
    missing_user = login_user(client, email="missing@example.com")

    assert wrong_password.status_code == 401
    assert missing_user.status_code == 401
    assert wrong_password.json()["detail"] == "Credenciais inválidas."
    assert missing_user.json()["detail"] == "Credenciais inválidas."


def test_protected_route_rejects_missing_and_invalid_token(client):
    missing = client.get("/auth/me")
    invalid = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_public_signup_cannot_choose_admin_role(client):
    response = register_user(client, tipo_usuario="admin")

    assert response.status_code == 422


def test_student_cannot_list_all_users(client):
    assert register_user(client).status_code == 201
    login = login_user(client)
    token = login.json()["data"]["access_token"]

    response = client.get(
        "/auth/usuarios",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_health_endpoint_is_public(client):
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
