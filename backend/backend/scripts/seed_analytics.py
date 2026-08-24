from __future__ import annotations

from datetime import datetime, timedelta, timezone

import app.models  # noqa: F401

from app.database import SessionLocal
from app.models.chat import ChatMessage, Conversation
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.user import Usuario
from scripts.seed_rbac import populate as populate_rbac

ANALYTICS_SEED_TAG = "[seed:analytics]"


def _pair(first_id: int, second_id: int) -> tuple[int, int]:
    return (first_id, second_id) if first_id < second_id else (second_id, first_id)


def populate(db) -> dict[str, int]:
    populate_rbac(db)
    now = datetime.now(timezone.utc)
    students = (
        db.query(Usuario)
        .filter(Usuario.tipo_usuario == "aluno", Usuario.email.like("%@seed.example.com"))
        .order_by(Usuario.id.asc())
        .all()
    )
    courses = db.query(Curso).order_by(Curso.id.asc()).limit(8).all()
    if len(students) < 4 or len(courses) < 4:
        raise RuntimeError("Advanced Search seed não forneceu dados suficientes para Analytics.")

    distinct_pairs = [
        (student, course)
        for student in students
        for course in courses
    ]
    if len(distinct_pairs) < 24:
        raise RuntimeError("Analytics precisa de pelo menos 24 pares aluno/curso distintos no seed.")

    statuses = ("ativa", "concluida", "cancelada")
    enrollment_count = 0
    for index, (student, course) in enumerate(distinct_pairs[:24]):
        enrollment = (
            db.query(Matricula)
            .filter(Matricula.aluno_id == student.id, Matricula.curso_id == course.id)
            .first()
        )
        if enrollment is None:
            enrollment = Matricula(aluno_id=student.id, curso_id=course.id)
            db.add(enrollment)

        status_value = statuses[index % len(statuses)]
        enrollment.status_matricula = status_value
        enrollment.data_matricula = now - timedelta(days=(index % 21), hours=index % 8)
        enrollment.data_conclusao = (
            enrollment.data_matricula + timedelta(days=2)
            if status_value == "concluida"
            else None
        )
        enrollment_count += 1
    db.flush()

    alice = next(user for user in students if user.email == "alice.ferreira@seed.example.com")
    camila = next(user for user in students if user.email == "camila.nunes@seed.example.com")
    low_id, high_id = _pair(alice.id, camila.id)
    conversation = (
        db.query(Conversation)
        .filter(Conversation.user_low_id == low_id, Conversation.user_high_id == high_id)
        .first()
    )
    if conversation is None:
        conversation = Conversation(user_low_id=low_id, user_high_id=high_id)
        db.add(conversation)
        db.flush()

    for index in range(6):
        content = f"{ANALYTICS_SEED_TAG} engagement {index + 1}"
        message = db.query(ChatMessage).filter(ChatMessage.content == content).first()
        if message is None:
            db.add(
                ChatMessage(
                    conversation_id=conversation.id,
                    sender_id=alice.id if index % 2 == 0 else camila.id,
                    content=content,
                    created_at=now - timedelta(days=index),
                )
            )
    conversation.updated_at = now
    db.commit()

    return {
        "students": len(students),
        "courses": len(courses),
        "enrollments": enrollment_count,
        "chat_messages": 6,
    }


def main() -> None:
    db = SessionLocal()
    try:
        counts = populate(db)
        print("Analytics seed population ready.")
        for key, value in counts.items():
            print(f"{key}: {value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
