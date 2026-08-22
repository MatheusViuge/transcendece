from app.database import SessionLocal
from app.models.course import Curso
from app.models.evaluation import AvaliacaoCurso
from app.models.user import Usuario
from scripts.seed_advanced_search import (
    COURSES,
    INSTRUCTORS,
    SEED_EMAIL_SUFFIX,
    SEED_TAG,
    STUDENTS,
    populate,
)


def test_advanced_search_manual_seed_is_idempotent_and_searchable(client):
    db = SessionLocal()
    try:
        first = populate(db)
        second = populate(db)

        assert first == second
        assert first["instructors"] == len(INSTRUCTORS)
        assert first["students"] == len(STUDENTS)
        assert first["courses"] == len(COURSES)

        seed_users = (
            db.query(Usuario)
            .filter(Usuario.email.like(f"%{SEED_EMAIL_SUFFIX}"))
            .count()
        )
        seed_courses = (
            db.query(Curso)
            .filter(Curso.descricao.like(f"{SEED_TAG}%"))
            .count()
        )
        seed_course_ids = [
            item.id
            for item in db.query(Curso.id)
            .filter(Curso.descricao.like(f"{SEED_TAG}%"))
            .all()
        ]
        seed_reviews = (
            db.query(AvaliacaoCurso)
            .filter(AvaliacaoCurso.curso_id.in_(seed_course_ids))
            .count()
        )

        assert seed_users == len(INSTRUCTORS) + len(STUDENTS)
        assert seed_courses == len(COURSES)
        assert seed_reviews == first["reviews"]
    finally:
        db.close()

    literal_percent = client.get(
        "/search/courses",
        params={"q": "100%", "page_size": 48},
    )
    assert literal_percent.status_code == 200
    assert [
        item["titulo"] for item in literal_percent.json()["data"]["items"]
    ] == ["APIs REST 100% Práticas"]

    paginated = client.get(
        "/search/courses",
        params={"page": 1, "page_size": 12, "sort": "title", "order": "asc"},
    )
    assert paginated.status_code == 200
    assert paginated.json()["data"]["pagination"]["total"] == len(COURSES)
    assert paginated.json()["data"]["pagination"]["total_pages"] == 3
