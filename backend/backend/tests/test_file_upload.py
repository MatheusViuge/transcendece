from pathlib import Path

from app.database import SessionLocal
from app.models.uploaded_file import UploadedFile
from scripts.seed_advanced_search import SEED_PASSWORD
from scripts.seed_rbac import RBAC_ADMIN_EMAIL, populate


def _seed() -> None:
    db = SessionLocal()
    try:
        populate(db)
    finally:
        db.close()


def _login(client, email: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "senha": SEED_PASSWORD})
    assert response.status_code == 200, response.text
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _upload(client, headers, name: str, content_type: str | None, content: bytes):
    return client.post(
        "/files",
        headers=headers,
        data={"purpose": "manual-test"},
        files={"file": (name, content, content_type)},
    )


def test_multiple_valid_types_upload_list_content_and_delete(client):
    _seed()
    headers = _login(client, "alice.ferreira@seed.example.com")
    samples = [
        ("imagem.png", "image/png", b"\x89PNG\r\n\x1a\nfile-upload-test"),
        ("documento.pdf", "application/pdf", b"%PDF-1.7\nfile-upload-test"),
        ("notas.txt", "text/plain", "conteúdo UTF-8 válido çã".encode()),
    ]

    ids = []
    for name, content_type, content in samples:
        response = _upload(client, headers, name, content_type, content)
        assert response.status_code == 201, response.text
        data = response.json()["data"]
        assert data["content_type"] == content_type
        assert data["content_url"].startswith("/api/files/")
        ids.append(data["id"])

    listing = client.get("/files", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()["data"]) == 3

    content = client.get(f"/files/{ids[0]}/content", headers=headers)
    assert content.status_code == 200
    assert content.headers["x-content-type-options"] == "nosniff"
    assert content.content.startswith(b"\x89PNG")

    deleted = client.delete(f"/files/{ids[0]}", headers=headers)
    assert deleted.status_code == 200
    assert client.get(f"/files/{ids[0]}", headers=headers).status_code == 404


def test_accepts_generic_browser_mime_but_stores_canonical_type(client):
    _seed()
    headers = _login(client, "alice.ferreira@seed.example.com")

    pdf = _upload(
        client,
        headers,
        "relatorio.pdf",
        "application/octet-stream",
        b"%PDF-1.7\nvalid browser fallback",
    )
    assert pdf.status_code == 201, pdf.text
    assert pdf.json()["data"]["content_type"] == "application/pdf"

    text = _upload(
        client,
        headers,
        "notas.txt",
        None,
        "texto UTF-8 válido çã".encode(),
    )
    assert text.status_code == 201, text.text
    assert text.json()["data"]["content_type"] == "text/plain"


def test_rejects_false_extension_signature_unsupported_and_oversized_files_without_garbage(client):
    _seed()
    headers = _login(client, "alice.ferreira@seed.example.com")

    wrong_extension = _upload(client, headers, "fake.jpg", "image/png", b"\x89PNG\r\n\x1a\nvalid")
    assert wrong_extension.status_code == 422

    wrong_signature = _upload(client, headers, "fake.png", "image/png", b"this is not png")
    assert wrong_signature.status_code == 422

    generic_wrong_signature = _upload(
        client,
        headers,
        "fake.pdf",
        "application/octet-stream",
        b"this is not a pdf",
    )
    assert generic_wrong_signature.status_code == 422

    unsupported = _upload(client, headers, "page.html", "text/html", b"unsupported html")
    assert unsupported.status_code == 415

    oversized = _upload(client, headers, "huge.txt", "text/plain", b"a" * (2 * 1024 * 1024 + 1))
    assert oversized.status_code == 413

    db = SessionLocal()
    try:
        assert db.query(UploadedFile).count() == 0
    finally:
        db.close()

    storage = Path("/tmp/transcendece_file_upload_tests")
    assert list(storage.iterdir()) == []


def test_filename_is_normalized_and_internal_path_is_server_generated(client):
    _seed()
    headers = _login(client, "alice.ferreira@seed.example.com")
    response = _upload(
        client,
        headers,
        "../../segredo.txt",
        "text/plain",
        b"safe content",
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["original_name"] == "segredo.txt"
    assert "storage_name" not in data

    db = SessionLocal()
    try:
        item = db.query(UploadedFile).filter(UploadedFile.id == data["id"]).one()
        assert ".." not in item.storage_name
        assert "/" not in item.storage_name
        assert item.storage_name != item.original_name
    finally:
        db.close()


def test_owner_isolation_and_admin_override(client):
    _seed()
    alice = _login(client, "alice.ferreira@seed.example.com")
    camila = _login(client, "camila.nunes@seed.example.com")
    admin = _login(client, RBAC_ADMIN_EMAIL)

    uploaded = _upload(client, alice, "private.pdf", "application/pdf", b"%PDF-1.7\nprivate")
    assert uploaded.status_code == 201
    file_id = uploaded.json()["data"]["id"]

    assert client.get(f"/files/{file_id}", headers=camila).status_code == 403
    assert client.get(f"/files/{file_id}/content", headers=camila).status_code == 403
    assert client.delete(f"/files/{file_id}", headers=camila).status_code == 403

    assert client.get(f"/files/{file_id}/content", headers=admin).status_code == 200
    assert client.delete(f"/files/{file_id}", headers=admin).status_code == 200
