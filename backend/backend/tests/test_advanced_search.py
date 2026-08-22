from datetime import date

from app.database import SessionLocal
from app.models.category import Categoria
from app.models.course import Curso
from app.models.evaluation import AvaliacaoCurso
from app.models.instructor import Instrutor
from app.models.level import Nivel
from app.models.user import Usuario


def _seed_search_catalog() -> dict[str, int]:
    db = SessionLocal()
    try:
        tech = Categoria(nome="Tecnologia", descricao="Cursos de tecnologia")
        design = Categoria(nome="Design", descricao="Cursos de design")
        beginner = Nivel(descricao="Iniciante")
        advanced = Nivel(descricao="Avançado")
        db.add_all([tech, design, beginner, advanced])

        ana = Usuario(
            nome="Ana",
            sobrenome="Silva",
            data_nascimento=date(1990, 1, 1),
            email="ana.search@example.com",
            senha_hash="hash",
            tipo_usuario="instrutor",
        )
        bruno = Usuario(
            nome="Bruno",
            sobrenome="Costa",
            data_nascimento=date(1991, 1, 1),
            email="bruno.search@example.com",
            senha_hash="hash",
            tipo_usuario="instrutor",
        )
        reviewer = Usuario(
            nome="Carla",
            sobrenome="Souza",
            data_nascimento=date(1992, 1, 1),
            email="carla.search@example.com",
            senha_hash="hash",
            tipo_usuario="aluno",
        )
        db.add_all([ana, bruno, reviewer])
        db.flush()

        db.add_all([
            Instrutor(id=ana.id, especialidade=1, biografia="Backend"),
            Instrutor(id=bruno.id, especialidade=1, biografia="Design"),
        ])
        db.flush()

        courses = [
            Curso(
                titulo="Introdução ao Python",
                descricao="Python para começar do zero",
                preco=0,
                carga_horaria=10,
                nivel_id=beginner.id,
                categoria_id=tech.id,
                instrutor_id=ana.id,
            ),
            Curso(
                titulo="Python Avançado",
                descricao="APIs e arquitetura avançada",
                preco=120,
                carga_horaria=20,
                nivel_id=advanced.id,
                categoria_id=tech.id,
                instrutor_id=ana.id,
            ),
            Curso(
                titulo="Python para Dados",
                descricao="Análise de dados persistidos",
                preco=180,
                carga_horaria=25,
                nivel_id=advanced.id,
                categoria_id=tech.id,
                instrutor_id=bruno.id,
            ),
            Curso(
                titulo="UX Essencial",
                descricao="Pesquisa e interfaces acessíveis",
                preco=90,
                carga_horaria=12,
                nivel_id=beginner.id,
                categoria_id=design.id,
                instrutor_id=bruno.id,
            ),
            Curso(
                titulo="100% Web",
                descricao="Caracteres especiais na busca",
                preco=75,
                carga_horaria=8,
                nivel_id=beginner.id,
                categoria_id=tech.id,
                instrutor_id=ana.id,
            ),
        ]
        db.add_all(courses)
        db.flush()

        db.add_all([
            AvaliacaoCurso(curso_id=courses[1].id, usuario_id=reviewer.id, nota=4),
            AvaliacaoCurso(curso_id=courses[2].id, usuario_id=reviewer.id, nota=5),
        ])
        db.commit()

        return {
            "tech": tech.id,
            "design": design.id,
            "beginner": beginner.id,
            "advanced": advanced.id,
            "ana": ana.id,
            "bruno": bruno.id,
        }
    finally:
        db.close()


def test_search_combines_filters_sorting_and_pagination(client):
    ids = _seed_search_catalog()

    response = client.get(
        "/search/courses",
        params={
            "q": "Python",
            "category_id": ids["tech"],
            "level_id": ids["advanced"],
            "price": "paid",
            "sort": "price",
            "order": "desc",
            "page": 1,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["pagination"] == {
        "page": 1,
        "page_size": 1,
        "total": 2,
        "total_pages": 2,
        "has_previous": False,
        "has_next": True,
    }
    assert [item["titulo"] for item in data["items"]] == ["Python para Dados"]
    assert data["items"][0]["avaliacao"] == 5.0
    assert any(item["label"] == "Tecnologia" for item in data["facets"]["categories"])


def test_search_pagination_is_deterministic_and_has_no_duplicates(client):
    _seed_search_catalog()

    first = client.get(
        "/search/courses",
        params={"sort": "title", "order": "asc", "page": 1, "page_size": 2},
    ).json()["data"]
    second = client.get(
        "/search/courses",
        params={"sort": "title", "order": "asc", "page": 2, "page_size": 2},
    ).json()["data"]

    first_ids = {item["id"] for item in first["items"]}
    second_ids = {item["id"] for item in second["items"]}
    assert first_ids.isdisjoint(second_ids)
    assert first["pagination"]["total"] == 5
    assert second["pagination"]["total_pages"] == 3


def test_search_handles_accents_and_literal_like_characters(client):
    _seed_search_catalog()

    accented = client.get("/search/courses", params={"q": "Introdução"})
    literal_percent = client.get("/search/courses", params={"q": "100%"})

    assert accented.status_code == 200
    assert [item["titulo"] for item in accented.json()["data"]["items"]] == ["Introdução ao Python"]
    assert literal_percent.status_code == 200
    assert [item["titulo"] for item in literal_percent.json()["data"]["items"]] == ["100% Web"]


def test_search_rejects_invalid_parameters(client):
    _seed_search_catalog()

    assert client.get("/search/courses", params={"page": 0}).status_code == 422
    assert client.get("/search/courses", params={"page_size": 49}).status_code == 422
    assert client.get("/search/courses", params={"sort": "drop-table"}).status_code == 422
    assert client.get("/search/courses", params={"price": "anything"}).status_code == 422
