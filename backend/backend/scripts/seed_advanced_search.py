from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import app.models  # noqa: F401 - register all SQLAlchemy models/relationships
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.category import Categoria
from app.models.course import Curso
from app.models.evaluation import AvaliacaoCurso
from app.models.instructor import Instrutor
from app.models.level import Nivel
from app.models.specialty import Especialidade
from app.models.user import Usuario
from app.services.auth_service import get_password_hash, verify_password

SEED_TAG = "[seed:advanced-search]"
SEED_PASSWORD = "SearchSeed42!"
SEED_EMAIL_SUFFIX = "@seed.example.com"

SPECIALTIES = [
    ("Backend & APIs", "APIs, arquitetura backend e integração de sistemas."),
    ("Ciência de Dados", "Análise, estatística, machine learning e bancos analíticos."),
    ("Frontend & UX", "Interfaces, design systems, acessibilidade e experiência do usuário."),
    ("DevOps & Cloud", "Containers, automação, infraestrutura e observabilidade."),
]

CATEGORIES = [
    ("Tecnologia", "Programação, APIs, ferramentas e engenharia de software."),
    ("Dados & IA", "Dados, analytics, machine learning e inteligência artificial."),
    ("Design & UX", "Design de interfaces, acessibilidade e experiência do usuário."),
    ("DevOps & Cloud", "Infraestrutura, containers, CI/CD e operação."),
    ("Negócios Digitais", "Produto, métricas, crescimento e estratégia técnica."),
]

LEVELS = ["Iniciante", "Intermediário", "Avançado"]

INSTRUCTORS = [
    {
        "nome": "Ana",
        "sobrenome": "Ribeiro",
        "email": "ana.ribeiro@seed.example.com",
        "data_nascimento": date(1988, 4, 12),
        "specialty": "Backend & APIs",
        "biografia": "Engenheira de software focada em Python, APIs e arquitetura backend.",
    },
    {
        "nome": "Bruno",
        "sobrenome": "Costa",
        "email": "bruno.costa@seed.example.com",
        "data_nascimento": date(1987, 9, 3),
        "specialty": "Ciência de Dados",
        "biografia": "Cientista de dados com experiência em analytics, SQL e machine learning.",
    },
    {
        "nome": "Carla",
        "sobrenome": "Mendes",
        "email": "carla.mendes@seed.example.com",
        "data_nascimento": date(1990, 2, 21),
        "specialty": "Frontend & UX",
        "biografia": "Product designer e frontend developer com foco em UX e acessibilidade.",
    },
    {
        "nome": "Diego",
        "sobrenome": "Santos",
        "email": "diego.santos@seed.example.com",
        "data_nascimento": date(1986, 11, 8),
        "specialty": "DevOps & Cloud",
        "biografia": "Especialista em containers, CI/CD, Linux, Nginx e observabilidade.",
    },
]

STUDENTS = [
    ("Alice", "Ferreira", "alice.ferreira@seed.example.com", date(1998, 1, 10)),
    ("Bernardo", "Lima", "bernardo.lima@seed.example.com", date(1997, 6, 22)),
    ("Camila", "Nunes", "camila.nunes@seed.example.com", date(2000, 3, 14)),
    ("Eduardo", "Rocha", "eduardo.rocha@seed.example.com", date(1996, 8, 30)),
    ("Fernanda", "Alves", "fernanda.alves@seed.example.com", date(1999, 5, 17)),
    ("Gabriel", "Barros", "gabriel.barros@seed.example.com", date(1995, 12, 9)),
    ("Helena", "Martins", "helena.martins@seed.example.com", date(2001, 7, 4)),
    ("Igor", "Pereira", "igor.pereira@seed.example.com", date(1998, 10, 26)),
]

COURSES = [
    ("Introdução ao Python", "Python para começar do zero com exercícios e fundamentos sólidos.", "Tecnologia", "Iniciante", "ana.ribeiro@seed.example.com", 0.0, 12),
    ("Python Avançado para APIs", "Python avançado, arquitetura, autenticação e integração de APIs.", "Tecnologia", "Avançado", "ana.ribeiro@seed.example.com", 149.90, 24),
    ("FastAPI na Prática", "Construa APIs REST com FastAPI, validação e persistência.", "Tecnologia", "Intermediário", "ana.ribeiro@seed.example.com", 119.90, 18),
    ("APIs REST 100% Práticas", "Curso 100% prático para testar caracteres especiais e busca textual.", "Tecnologia", "Intermediário", "ana.ribeiro@seed.example.com", 0.0, 16),
    ("C++ Moderno: do Zero ao Avançado", "C++ moderno, memória, STL e boas práticas de engenharia.", "Tecnologia", "Avançado", "ana.ribeiro@seed.example.com", 179.90, 30),
    ("Git & GitHub para Times", "Versionamento, branches, pull requests e colaboração em equipe.", "Tecnologia", "Iniciante", "ana.ribeiro@seed.example.com", 49.90, 8),
    ("Ciência de Dados com Python", "Pipeline de análise de dados com Python e notebooks reproduzíveis.", "Dados & IA", "Intermediário", "bruno.costa@seed.example.com", 199.90, 28),
    ("SQL para Análise de Dados", "Consultas SQL, agregações, joins e exploração de dados.", "Dados & IA", "Iniciante", "bruno.costa@seed.example.com", 0.0, 14),
    ("Machine Learning Essencial", "Modelos supervisionados, métricas e validação de machine learning.", "Dados & IA", "Avançado", "bruno.costa@seed.example.com", 249.90, 32),
    ("Estatística Aplicada à IA", "Probabilidade, inferência e estatística aplicada a produtos de IA.", "Dados & IA", "Intermediário", "bruno.costa@seed.example.com", 129.90, 20),
    ("Pandas: Limpeza e Exploração", "Tratamento, transformação e exploração de dados com Pandas.", "Dados & IA", "Iniciante", "bruno.costa@seed.example.com", 79.90, 12),
    ("PostgreSQL para Analytics", "Modelagem, índices e consultas analíticas com PostgreSQL.", "Dados & IA", "Avançado", "bruno.costa@seed.example.com", 159.90, 22),
    ("UX Essencial: Pesquisa e Personas", "Pesquisa com usuários, personas e jornadas para produtos digitais.", "Design & UX", "Iniciante", "carla.mendes@seed.example.com", 0.0, 10),
    ("UI Design com Design Systems", "Componentes, tokens e consistência visual com design systems.", "Design & UX", "Intermediário", "carla.mendes@seed.example.com", 139.90, 18),
    ("Acessibilidade Web na Prática", "Semântica, teclado, contraste e acessibilidade para interfaces web.", "Design & UX", "Intermediário", "carla.mendes@seed.example.com", 89.90, 14),
    ("Figma do Zero ao Protótipo", "Wireframes, componentes e protótipos navegáveis no Figma.", "Design & UX", "Iniciante", "carla.mendes@seed.example.com", 69.90, 12),
    ("Product Design Avançado", "Discovery, experimentação e decisões de product design orientadas a dados.", "Design & UX", "Avançado", "carla.mendes@seed.example.com", 189.90, 26),
    ("CSS Responsivo & Interfaces Modernas", "Layouts responsivos, Grid, Flexbox e interfaces modernas.", "Design & UX", "Intermediário", "carla.mendes@seed.example.com", 99.90, 16),
    ("Docker do Zero", "Imagens, containers, volumes e redes para começar com Docker.", "DevOps & Cloud", "Iniciante", "diego.santos@seed.example.com", 0.0, 10),
    ("Docker Compose para Ambientes Reais", "Orquestração local, dependências e healthchecks com Compose.", "DevOps & Cloud", "Intermediário", "diego.santos@seed.example.com", 99.90, 16),
    ("Nginx, HTTPS e Reverse Proxy", "Nginx, TLS, proxy reverso e headers para aplicações web.", "DevOps & Cloud", "Avançado", "diego.santos@seed.example.com", 129.90, 18),
    ("CI/CD com GitHub Actions", "Pipelines automatizados de lint, testes, build e deployment.", "DevOps & Cloud", "Intermediário", "diego.santos@seed.example.com", 119.90, 18),
    ("Kubernetes: Fundamentos", "Pods, deployments, services e conceitos fundamentais de Kubernetes.", "DevOps & Cloud", "Avançado", "diego.santos@seed.example.com", 199.90, 28),
    ("Linux para DevOps", "Shell, processos, permissões, logs e diagnóstico em Linux.", "DevOps & Cloud", "Iniciante", "diego.santos@seed.example.com", 59.90, 12),
    ("Métricas de Produto para Devs", "Métricas de produto, funil e retenção para equipes técnicas.", "Negócios Digitais", "Iniciante", "carla.mendes@seed.example.com", 79.90, 10),
    ("Analytics para Produtos Digitais", "Eventos, métricas e análise de comportamento em produtos digitais.", "Negócios Digitais", "Intermediário", "bruno.costa@seed.example.com", 139.90, 16),
    ("Arquitetura SaaS: do MVP à Escala", "Decisões técnicas para evoluir um SaaS do MVP à escala.", "Negócios Digitais", "Avançado", "ana.ribeiro@seed.example.com", 229.90, 24),
    ("Observabilidade e SRE para Produtos", "SLIs, SLOs, logs, métricas e operação confiável de produtos.", "Negócios Digitais", "Avançado", "diego.santos@seed.example.com", 189.90, 22),
    ("SEO Técnico para Aplicações Web", "SEO técnico, performance e indexação para aplicações modernas.", "Negócios Digitais", "Intermediário", "carla.mendes@seed.example.com", 0.0, 12),
    ("Estratégia de APIs como Produto", "Governança, versionamento e estratégia de APIs como produto.", "Negócios Digitais", "Avançado", "ana.ribeiro@seed.example.com", 159.90, 20),
]


def _upsert_user(
    db: Session,
    *,
    nome: str,
    sobrenome: str,
    email: str,
    data_nascimento: date,
    role: str,
) -> Usuario:
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        user = Usuario(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            data_nascimento=data_nascimento,
            tipo_usuario=role,
            senha_hash=get_password_hash(SEED_PASSWORD),
        )
        db.add(user)
    else:
        user.nome = nome
        user.sobrenome = sobrenome
        user.data_nascimento = data_nascimento
        user.tipo_usuario = role
        if not verify_password(SEED_PASSWORD, user.senha_hash):
            user.senha_hash = get_password_hash(SEED_PASSWORD)

    db.flush()
    return user


def populate(db: Session) -> dict[str, int]:
    try:
        specialties: dict[str, Especialidade] = {}
        for name, description in SPECIALTIES:
            item = db.query(Especialidade).filter(Especialidade.nome == name).first()
            if item is None:
                item = Especialidade(nome=name, descricao=description)
                db.add(item)
            specialties[name] = item
        db.flush()

        categories: dict[str, Categoria] = {}
        for name, description in CATEGORIES:
            item = db.query(Categoria).filter(Categoria.nome == name).first()
            if item is None:
                item = Categoria(nome=name, descricao=description)
                db.add(item)
            categories[name] = item
        db.flush()

        levels: dict[str, Nivel] = {}
        for description in LEVELS:
            item = db.query(Nivel).filter(Nivel.descricao == description).first()
            if item is None:
                item = Nivel(descricao=description)
                db.add(item)
            levels[description] = item
        db.flush()

        instructors: dict[str, Usuario] = {}
        for data in INSTRUCTORS:
            user = _upsert_user(
                db,
                nome=data["nome"],
                sobrenome=data["sobrenome"],
                email=data["email"],
                data_nascimento=data["data_nascimento"],
                role="instrutor",
            )
            instructor = db.query(Instrutor).filter(Instrutor.id == user.id).first()
            if instructor is None:
                instructor = Instrutor(id=user.id)
                db.add(instructor)
            instructor.especialidade = specialties[data["specialty"]].id
            instructor.biografia = data["biografia"]
            instructors[user.email] = user
        db.flush()

        students: list[Usuario] = []
        for nome, sobrenome, email, birth_date in STUDENTS:
            students.append(
                _upsert_user(
                    db,
                    nome=nome,
                    sobrenome=sobrenome,
                    email=email,
                    data_nascimento=birth_date,
                    role="aluno",
                )
            )
        db.flush()

        courses: list[Curso] = []
        base_date = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
        for index, (
            title,
            description,
            category,
            level,
            instructor_email,
            price,
            hours,
        ) in enumerate(COURSES):
            instructor_id = instructors[instructor_email].id
            tagged_description = f"{SEED_TAG} {description}"
            course = (
                db.query(Curso)
                .filter(
                    Curso.titulo == title,
                    Curso.instrutor_id == instructor_id,
                    Curso.descricao.like(f"{SEED_TAG}%"),
                )
                .first()
            )
            created_at = base_date + timedelta(days=index * 4)
            if course is None:
                course = Curso(
                    titulo=title,
                    descricao=tagged_description,
                    preco=price,
                    carga_horaria=hours,
                    categoria_id=categories[category].id,
                    nivel_id=levels[level].id,
                    instrutor_id=instructor_id,
                    data_criacao=created_at,
                    ultima_atualizacao=created_at,
                )
                db.add(course)
            else:
                course.descricao = tagged_description
                course.preco = price
                course.carga_horaria = hours
                course.categoria_id = categories[category].id
                course.nivel_id = levels[level].id
                course.data_criacao = created_at
                course.ultima_atualizacao = created_at
            courses.append(course)
        db.flush()

        seed_course_ids = [course.id for course in courses]
        seed_student_ids = [student.id for student in students]
        (
            db.query(AvaliacaoCurso)
            .filter(
                AvaliacaoCurso.curso_id.in_(seed_course_ids),
                AvaliacaoCurso.usuario_id.in_(seed_student_ids),
            )
            .delete(synchronize_session=False)
        )

        reviews = 0
        for course_index, course in enumerate(courses):
            # A cada cinco cursos, deixa um sem reviews para também testar rating 0.
            if course_index % 5 == 0:
                continue
            review_count = 2 + (course_index % 3)
            for offset in range(review_count):
                student = students[(course_index + offset) % len(students)]
                rating = 1 + ((course_index + offset * 2) % 5)
                db.add(
                    AvaliacaoCurso(
                        curso_id=course.id,
                        usuario_id=student.id,
                        nota=rating,
                        comentario=f"{SEED_TAG} Avaliação determinística para teste manual.",
                    )
                )
                reviews += 1

        db.commit()
        return {
            "specialties": len(SPECIALTIES),
            "categories": len(CATEGORIES),
            "levels": len(LEVELS),
            "instructors": len(INSTRUCTORS),
            "students": len(STUDENTS),
            "courses": len(COURSES),
            "reviews": reviews,
        }
    except Exception:
        db.rollback()
        raise


def main() -> None:
    db = SessionLocal()
    try:
        summary = populate(db)
    finally:
        db.close()

    print("Advanced Search seed concluído.")
    print(
        "Criados/reutilizados: "
        f"{summary['instructors']} instrutores, "
        f"{summary['students']} alunos, "
        f"{summary['courses']} cursos e "
        f"{summary['reviews']} avaliações."
    )
    print(f"Senha de todas as contas seed: {SEED_PASSWORD}")
    print("Instrutores:")
    for item in INSTRUCTORS:
        print(f"  - {item['email']}")
    print("Alunos:")
    for _, _, email, _ in STUDENTS:
        print(f"  - {email}")


if __name__ == "__main__":
    main()
