from app.services.auth_service import get_password_hash, verify_password


def test_password_hash_does_not_store_plain_text():
    password = "SenhaForte#123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert password not in hashed
    assert verify_password(password, hashed) is True


def test_same_password_generates_different_hashes():
    password = "SenhaForte#123"

    first_hash = get_password_hash(password)
    second_hash = get_password_hash(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True


def test_wrong_password_is_rejected():
    hashed = get_password_hash("SenhaCorreta#123")

    assert verify_password("SenhaErrada#123", hashed) is False


def test_invalid_hash_is_rejected_without_crashing():
    assert verify_password("qualquer-senha", "not-a-valid-passlib-hash") is False
