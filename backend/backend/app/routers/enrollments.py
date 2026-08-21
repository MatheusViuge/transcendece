from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.models.course import Curso
from app.models.enrollment import Matricula
from app.models.instructor import Instrutor
from app.models.lesson import Aula
from app.models.module import Modulo
from app.models.progress import ProgressoAulas
from app.models.user import Usuario
from app.schemas.enrollment import EnrollmentCreate, EnrollmentStatus

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])
PositivePathId = Annotated[int, Path(gt=0)]


def check_enrollment_access(
    matricula: Matricula,
    usuario: dict,
    db: Session,
    resource: str = "enrollment",
) -> None:
    role = usuario.get("role")
    user_id = usuario.get("id")

    if role == "admin":
        return

    if role == "aluno" and matricula.aluno_id == user_id:
        return

    if role == "instrutor":
        curso = db.query(Curso).filter(Curso.id == matricula.curso_id).first()
        if curso and curso.instrutor_id == user_id:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Acesso negado a este {resource}.",
    )


def serialize_enrollment(matricula: Matricula, db: Session) -> dict:
    aluno = db.query(Usuario).filter(Usuario.id == matricula.aluno_id).first()
    curso = db.query(Curso).filter(Curso.id == matricula.curso_id).first()
    instrutor = None
    usuario_instrutor = None

    if curso:
        instrutor = db.query(Instrutor).filter(Instrutor.id == curso.instrutor_id).first()
        if instrutor:
            usuario_instrutor = db.query(Usuario).filter(Usuario.id == instrutor.id).first()

    return {
        "id": matricula.id,
        "id_aluno": matricula.aluno_id,
        "aluno": f"{aluno.nome} {aluno.sobrenome}" if aluno else "",
        "id_curso": matricula.curso_id,
        "curso": curso.titulo if curso else "",
        "id_instrutor": curso.instrutor_id if curso else None,
        "instrutor": (
            f"{usuario_instrutor.nome} {usuario_instrutor.sobrenome}"
            if usuario_instrutor
            else ""
        ),
        "status_matricula": matricula.status_matricula,
        "data_conclusao": matricula.data_conclusao,
    }


@router.get("/")
def list_enrollments(
    id_curso: Annotated[Optional[int], Query(gt=0)] = None,
    id_aluno: Annotated[Optional[int], Query(gt=0)] = None,
    enrollment_status: Annotated[Optional[EnrollmentStatus], Query(alias="status")] = None,
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles("aluno", "instrutor", "admin")),
):
    role = usuario["role"]
    user_id = usuario["id"]
    query = db.query(Matricula)

    if role == "aluno":
        query = query.filter(Matricula.aluno_id == user_id)
    elif role == "instrutor":
        curso_ids = [
            curso.id
            for curso in db.query(Curso).filter(Curso.instrutor_id == user_id).all()
        ]
        if not curso_ids:
            return success_response(
                data=[],
                message="Nenhuma matrícula encontrada para este instrutor.",
            )
        query = query.filter(Matricula.curso_id.in_(curso_ids))

    if id_curso is not None:
        query = query.filter(Matricula.curso_id == id_curso)

    if id_aluno is not None:
        if role == "aluno" and id_aluno != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado a outro aluno.")
        query = query.filter(Matricula.aluno_id == id_aluno)

    if enrollment_status is not None:
        query = query.filter(Matricula.status_matricula == enrollment_status)

    matriculas = query.all()
    return success_response(
        data=[serialize_enrollment(item, db) for item in matriculas],
        message="Matrículas listadas com sucesso.",
    )


@router.get("/{enrollment_id}/progress")
def get_enrollment_progress(
    enrollment_id: PositivePathId,
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles("aluno", "instrutor", "admin")),
):
    matricula = db.query(Matricula).filter(Matricula.id == enrollment_id).first()
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")

    check_enrollment_access(matricula, usuario, db, "matrícula")

    aluno = db.query(Usuario).filter(Usuario.id == matricula.aluno_id).first()
    curso = db.query(Curso).filter(Curso.id == matricula.curso_id).first()
    instrutor = (
        db.query(Instrutor).filter(Instrutor.id == curso.instrutor_id).first()
        if curso
        else None
    )
    usuario_instrutor = (
        db.query(Usuario).filter(Usuario.id == instrutor.id).first()
        if instrutor
        else None
    )

    modulos = (
        db.query(Modulo)
        .filter(Modulo.curso_id == matricula.curso_id)
        .order_by(Modulo.ordem)
        .all()
    )

    aulas_list = []
    total_aulas = 0
    aulas_concluidas = 0

    for modulo in modulos:
        aulas = (
            db.query(Aula)
            .filter(Aula.modulo_id == modulo.id)
            .order_by(Aula.ordem_aula)
            .all()
        )
        for aula in aulas:
            total_aulas += 1
            progresso = (
                db.query(ProgressoAulas)
                .filter(
                    ProgressoAulas.matricula_id == enrollment_id,
                    ProgressoAulas.aula_id == aula.id,
                )
                .first()
            )
            if progresso and progresso.concluido:
                aulas_concluidas += 1

            aulas_list.append(
                {
                    "id_aula": aula.id,
                    "titulo_aula": aula.titulo,
                    "ordem_aula": aula.ordem_aula,
                    "id_modulo": modulo.id,
                    "titulo_modulo": modulo.titulo,
                    "ordem_modulo": modulo.ordem,
                    "progresso_aula": progresso.progresso_percentual if progresso else 0,
                    "concluido": progresso.concluido if progresso else False,
                    "data_conclusao": progresso.data_conclusao if progresso else None,
                }
            )

    progresso_curso = (aulas_concluidas / total_aulas * 100) if total_aulas else 0
    data = serialize_enrollment(matricula, db)
    data.update(
        {
            "aluno": f"{aluno.nome} {aluno.sobrenome}" if aluno else "",
            "instrutor": (
                f"{usuario_instrutor.nome} {usuario_instrutor.sobrenome}"
                if usuario_instrutor
                else ""
            ),
            "progresso_curso": round(progresso_curso, 2),
            "aulas": aulas_list,
        }
    )

    return success_response(
        data=data,
        message="Progresso da matrícula retornado com sucesso.",
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles("aluno", "instrutor", "admin")),
):
    role = usuario["role"]
    user_id = usuario["id"]

    curso = db.query(Curso).filter(Curso.id == payload.id_curso).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    if role == "aluno":
        if payload.id_aluno is not None and payload.id_aluno != user_id:
            raise HTTPException(status_code=403, detail="Aluno não pode matricular outro usuário.")
        id_aluno = user_id
    else:
        if payload.id_aluno is None:
            raise HTTPException(status_code=422, detail="id_aluno é obrigatório para esta role.")
        id_aluno = payload.id_aluno

    if role == "instrutor" and curso.instrutor_id != user_id:
        raise HTTPException(status_code=403, detail="Instrutor só pode matricular em seus cursos.")

    aluno = db.query(Usuario).filter(Usuario.id == id_aluno).first()
    if not aluno or aluno.tipo_usuario != "aluno":
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")

    existente = (
        db.query(Matricula)
        .filter(Matricula.curso_id == payload.id_curso, Matricula.aluno_id == id_aluno)
        .with_for_update()
        .first()
    )

    if existente:
        if existente.status_matricula == "ativa":
            raise HTTPException(status_code=409, detail="Aluno já possui matrícula ativa neste curso.")
        existente.status_matricula = "ativa"
        existente.data_conclusao = None
        existente.data_matricula = datetime.now(timezone.utc)
        matricula = existente
    else:
        matricula = Matricula(
            aluno_id=id_aluno,
            curso_id=payload.id_curso,
            status_matricula="ativa",
        )
        db.add(matricula)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflito de matrícula. A operação foi executada simultaneamente.",
        )

    db.refresh(matricula)
    return success_response(
        data=serialize_enrollment(matricula, db),
        message="Matrícula criada com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/{enrollment_id}")
def delete_enrollment(
    enrollment_id: PositivePathId,
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles("aluno", "instrutor", "admin")),
):
    matricula = (
        db.query(Matricula)
        .filter(Matricula.id == enrollment_id)
        .with_for_update()
        .first()
    )
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")

    check_enrollment_access(matricula, usuario, db, "matrícula")
    matricula.status_matricula = "cancelada"
    matricula.data_conclusao = None
    db.commit()

    return success_response(data=None, message="Matrícula cancelada com sucesso.")


@router.patch("/{enrollment_id}/classes/{class_id}/toggle")
def toggle_class(
    enrollment_id: PositivePathId,
    class_id: PositivePathId,
    db: Session = Depends(get_db),
    usuario=Depends(allowed_roles("aluno", "instrutor", "admin")),
):
    matricula = db.query(Matricula).filter(Matricula.id == enrollment_id).first()
    if not matricula:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada.")

    check_enrollment_access(matricula, usuario, db, "matrícula")

    aula = db.query(Aula).filter(Aula.id == class_id).first()
    if not aula or not aula.modulo or aula.modulo.curso_id != matricula.curso_id:
        raise HTTPException(status_code=404, detail="Aula não pertence ao curso da matrícula.")

    progresso = (
        db.query(ProgressoAulas)
        .filter(
            ProgressoAulas.matricula_id == enrollment_id,
            ProgressoAulas.aula_id == class_id,
        )
        .with_for_update()
        .first()
    )

    if not progresso:
        progresso = ProgressoAulas(
            matricula_id=enrollment_id,
            aula_id=class_id,
            progresso_percentual=100,
            concluido=True,
            data_conclusao=datetime.now(timezone.utc),
        )
        db.add(progresso)
        message = "Aula marcada como concluída."
    else:
        progresso.concluido = not progresso.concluido
        progresso.progresso_percentual = 100 if progresso.concluido else 0
        progresso.data_conclusao = datetime.now(timezone.utc) if progresso.concluido else None
        message = (
            "Aula marcada como concluída."
            if progresso.concluido
            else "Aula desmarcada como concluída."
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflito de progresso. Recarregue o estado e tente novamente.",
        )

    return success_response(
        data={
            "id_aula": class_id,
            "concluido": progresso.concluido,
            "progresso_percentual": progresso.progresso_percentual,
            "data_conclusao": progresso.data_conclusao,
        },
        message=message,
    )
