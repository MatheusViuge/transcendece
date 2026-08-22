from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.rbac import Permission, has_permission, require_permissions
from app.core.response import success_response
from app.core.security import current_user
from app.database import get_db
from app.models.course import Curso
from app.models.evaluation import AvaliacaoCurso
from app.models.instructor import Instrutor
from app.schemas.course import (
    CursoControleAtualizar,
    CursoControleCriar,
    CursoControleResponse,
    CursoEspecificoResponse,
    CursoEstatisticaItem,
    CursoResponse,
)

router = APIRouter(prefix="/courses", tags=["courses"])
precoList = Literal["pago", "gratuito"]


def _ensure_instructor(db: Session, instructor_id: int) -> Instrutor:
    instructor = db.query(Instrutor).filter(Instrutor.id == instructor_id).first()
    if instructor is None:
        raise HTTPException(status_code=422, detail="Instrutor informado não existe.")
    return instructor


def _require_course_access(
    usuario: dict,
    curso: Curso,
    *,
    own_permission: Permission,
    any_permission: Permission,
) -> None:
    role = usuario["role"]
    if has_permission(role, any_permission):
        return
    if curso.instrutor_id == usuario["id"] and has_permission(role, own_permission):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para acessar este recurso do curso.",
    )


@router.get("/", response_model=List[CursoResponse])
def listar_cursos(
    id_categoria: int = 0,
    id_nivel: int = 0,
    preco: precoList | None = None,
    db: Session = Depends(get_db),
):
    del id_categoria, id_nivel, preco
    resultados = (
        db.query(
            Curso,
            func.coalesce(func.avg(AvaliacaoCurso.nota), 0).label("avaliacao_media"),
            func.count(AvaliacaoCurso.id).label("quantidade_avaliacoes"),
        )
        .outerjoin(AvaliacaoCurso, AvaliacaoCurso.curso_id == Curso.id)
        .group_by(Curso.id)
        .all()
    )
    resposta = [
        CursoResponse(
            id=curso.id,
            url_image=getattr(curso, "url_image", None),
            titulo=curso.titulo,
            id_instrutor=curso.instrutor_id,
            instrutor=curso.instrutor.usuario.nome,
            id_nivel=curso.nivel_id,
            nivel=curso.nivel.descricao,
            avaliacao=float(avaliacao_media or 0.0),
            quantidade_avaliacoes=int(qtd_avaliacoes or 0),
            preco=curso.preco or 0.0,
        )
        for curso, avaliacao_media, qtd_avaliacoes in resultados
    ]
    return success_response(data=resposta, message="Cursos listados com sucesso.")


@router.get("/{id_curso}", response_model=CursoEspecificoResponse)
def pegar_curso(id_curso: int, db: Session = Depends(get_db)):
    resultado = (
        db.query(
            Curso,
            func.coalesce(func.avg(AvaliacaoCurso.nota), 0).label("avaliacao_media"),
            func.count(AvaliacaoCurso.id).label("quantidade_avaliacoes"),
        )
        .outerjoin(AvaliacaoCurso, AvaliacaoCurso.curso_id == Curso.id)
        .filter(Curso.id == id_curso)
        .group_by(Curso.id)
        .first()
    )
    if not resultado:
        raise HTTPException(status_code=404, detail=f"Curso com id {id_curso} não encontrado")
    curso, avaliacao_media, qtd_avaliacoes = resultado
    return success_response(
        data=CursoEspecificoResponse(
            id=curso.id,
            titulo=curso.titulo,
            descricao=curso.descricao,
            avaliacao=float(avaliacao_media or 0.0),
            quantidade_avaliacoes=int(qtd_avaliacoes or 0),
            quantidade_horas=curso.carga_horaria,
            id_nivel=curso.nivel_id,
            nivel=curso.nivel.descricao,
            preco=curso.preco,
            id_instrutor=curso.instrutor_id,
            instrutor=curso.instrutor.usuario.nome,
            id_especialidade=curso.instrutor.especialidade,
            especialidade_instrutor=curso.instrutor.especialidade_rel.nome,
        ),
        message="Curso encontrado com sucesso.",
    )


@router.post("", response_model=CursoControleResponse, status_code=status.HTTP_201_CREATED)
def criar_curso(
    curso_in: CursoControleCriar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(require_permissions(Permission.COURSE_CREATE)),
):
    instructor_id = usuario["id"] if usuario["role"] == "instrutor" else curso_in.id_instrutor
    if instructor_id is None:
        raise HTTPException(status_code=422, detail="id_instrutor é obrigatório para administradores.")
    _ensure_instructor(db, instructor_id)

    novo_curso = Curso(
        titulo=curso_in.titulo,
        descricao=curso_in.descricao,
        categoria_id=curso_in.id_categoria,
        nivel_id=curso_in.id_nivel,
        instrutor_id=instructor_id,
        preco=curso_in.preco if curso_in.preco is not None else 0.0,
        carga_horaria=1,
    )
    db.add(novo_curso)
    db.commit()
    db.refresh(novo_curso)
    return CursoControleResponse(
        id=novo_curso.id,
        titulo=novo_curso.titulo,
        descricao=novo_curso.descricao,
        id_categoria=novo_curso.categoria_id,
        id_nivel=novo_curso.nivel_id,
        id_instrutor=novo_curso.instrutor_id,
        preco=novo_curso.preco,
    )


@router.put("/{curso_id}", response_model=CursoControleResponse)
def atualizar_curso(
    curso_id: int,
    curso_in: CursoControleAtualizar,
    db: Session = Depends(get_db),
    usuario: dict = Depends(current_user),
):
    if curso_in.id != curso_id:
        raise HTTPException(status_code=400, detail="ID do corpo da requisição é diferente do ID da URL.")

    curso_db = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso_db:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    _require_course_access(
        usuario,
        curso_db,
        own_permission=Permission.COURSE_UPDATE_OWN,
        any_permission=Permission.COURSE_UPDATE_ANY,
    )

    curso_db.titulo = curso_in.titulo
    curso_db.descricao = curso_in.descricao
    curso_db.categoria_id = curso_in.id_categoria
    curso_db.nivel_id = curso_in.id_nivel
    curso_db.preco = curso_in.preco if curso_in.preco is not None else 0.0

    if has_permission(usuario["role"], Permission.COURSE_UPDATE_ANY):
        if curso_in.id_instrutor is None:
            raise HTTPException(status_code=422, detail="id_instrutor é obrigatório para administradores.")
        _ensure_instructor(db, curso_in.id_instrutor)
        curso_db.instrutor_id = curso_in.id_instrutor
    else:
        curso_db.instrutor_id = usuario["id"]

    db.commit()
    db.refresh(curso_db)
    return CursoControleResponse(
        id=curso_db.id,
        titulo=curso_db.titulo,
        descricao=curso_db.descricao,
        id_categoria=curso_db.categoria_id,
        id_nivel=curso_db.nivel_id,
        id_instrutor=curso_db.instrutor_id,
        preco=curso_db.preco,
        sobre=0.0,
    )


@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(current_user),
):
    curso_db = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso_db:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    _require_course_access(
        usuario,
        curso_db,
        own_permission=Permission.COURSE_DELETE_OWN,
        any_permission=Permission.COURSE_DELETE_ANY,
    )

    if curso_db.modulos:
        raise HTTPException(
            status_code=403,
            detail="Curso não pode ser deletado porque já possui módulos (não é mais rascunho).",
        )

    db.delete(curso_db)
    db.commit()
    return


@router.get("/{curso_id}/statistics", response_model=List[CursoEstatisticaItem])
def estatisticas_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    usuario: dict = Depends(current_user),
):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    _require_course_access(
        usuario,
        curso,
        own_permission=Permission.COURSE_STATS_OWN,
        any_permission=Permission.COURSE_STATS_ANY,
    )

    categoria = curso.categoria.descricao if curso.categoria else ""
    nivel = curso.nivel.descricao if curso.nivel else ""
    instrutor = curso.instrutor.usuario.nome if curso.instrutor else ""

    media_notas = db.query(func.avg(AvaliacaoCurso.nota)).filter(AvaliacaoCurso.curso_id == curso_id).scalar()
    media_notas = float(media_notas) if media_notas else 0.0

    matriculas = curso.matriculas or []
    quantidade_alunos = len(matriculas)
    total_aulas = sum(len(modulo.aulas or []) for modulo in curso.modulos or [])
    percentual_medio = 0.0

    if quantidade_alunos > 0 and total_aulas > 0:
        percentuais = []
        for matricula in matriculas:
            progresso = matricula.progresso_aulas or []
            aulas_concluidas = sum(1 for item in progresso if item.concluido)
            percentuais.append((aulas_concluidas / total_aulas) * 100)
        if percentuais:
            percentual_medio = sum(percentuais) / len(percentuais)

    return [
        CursoEstatisticaItem(
            id=curso.id,
            titulo=curso.titulo,
            id_categoria=curso.categoria_id,
            categoria=categoria,
            id_nivel=curso.nivel_id,
            nivel=nivel,
            id_instrutor=curso.instrutor_id,
            instrutor=instrutor,
            percentual_conclusao=percentual_medio,
            media_notas=media_notas,
            quantidade_alunos=quantidade_alunos,
            data_criacao=curso.data_criacao,
            data_publicacao=None,
        )
    ]
