from sqlalchemy import UniqueConstraint

from app.models.enrollment import Matricula
from app.models.progress import ProgressoAulas
from app.schemas.enrollment import EnrollmentCreate


def test_enrollment_has_unique_student_course_constraint():
    constraints = [
        constraint
        for constraint in Matricula.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert any(
        constraint.name == "uq_matriculas_aluno_curso"
        and {column.name for column in constraint.columns} == {"aluno_id", "curso_id"}
        for constraint in constraints
    )


def test_progress_primary_key_prevents_duplicate_lesson_state():
    primary_key_columns = {column.name for column in ProgressoAulas.__table__.primary_key.columns}

    assert primary_key_columns == {"matricula_id", "aula_id"}


def test_enrollment_input_rejects_invalid_ids_and_extra_fields():
    valid = EnrollmentCreate.model_validate({"id_curso": 1})
    assert valid.id_curso == 1

    for payload in (
        {"id_curso": 0},
        {"id_curso": -1},
        {"id_curso": 1, "role": "admin"},
    ):
        try:
            EnrollmentCreate.model_validate(payload)
        except Exception:
            pass
        else:
            raise AssertionError(f"Payload deveria ser rejeitado: {payload}")
