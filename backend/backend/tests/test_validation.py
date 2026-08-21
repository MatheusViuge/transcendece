from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.evaluation import AvaliacaoCriar
from app.schemas.user import UsuarioCriar


VALID_PASSWORD = "SenhaForte#123"


def valid_user_payload():
    return {
        "nome": "Matheus",
        "sobrenome": "Silva",
        "email": "user@example.com",
        "senha_hash": VALID_PASSWORD,
        "data_nascimento": date.today() - timedelta(days=365 * 18),
    }


def test_public_registration_rejects_role_mass_assignment():
    payload = valid_user_payload()
    payload["tipo_usuario"] = "admin"

    with pytest.raises(ValidationError):
        UsuarioCriar.model_validate(payload)


def test_registration_rejects_unknown_fields():
    payload = valid_user_payload()
    payload["is_admin"] = True

    with pytest.raises(ValidationError):
        UsuarioCriar.model_validate(payload)


def test_registration_rejects_future_birth_date():
    payload = valid_user_payload()
    payload["data_nascimento"] = date.today() + timedelta(days=1)

    with pytest.raises(ValidationError):
        UsuarioCriar.model_validate(payload)


def test_registration_rejects_weak_password():
    payload = valid_user_payload()
    payload["senha_hash"] = "abcdef"

    with pytest.raises(ValidationError):
        UsuarioCriar.model_validate(payload)


def test_review_rejects_user_and_course_ids_in_body():
    with pytest.raises(ValidationError):
        AvaliacaoCriar.model_validate(
            {"nota": 5, "comentario": "Ótimo", "usuario_id": 999, "curso_id": 999}
        )


def test_review_accepts_only_expected_fields():
    review = AvaliacaoCriar.model_validate({"nota": 5, "comentario": "Ótimo"})

    assert review.nota == 5
    assert review.comentario == "Ótimo"
