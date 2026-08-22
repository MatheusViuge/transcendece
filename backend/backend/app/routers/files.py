from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import current_user
from app.database import get_db
from app.models.uploaded_file import UploadedFile
from app.services.file_storage import persist_upload, remove_stored_file, stored_path

router = APIRouter(prefix="/files", tags=["files"])


def _serialize(item: UploadedFile) -> dict[str, object]:
    return {
        "id": item.id,
        "original_name": item.original_name,
        "content_type": item.content_type,
        "size_bytes": item.size_bytes,
        "sha256": item.sha256,
        "purpose": item.purpose,
        "created_at": item.created_at,
        "content_url": f"/api/files/{item.id}/content",
    }


def _owned_or_admin(db: Session, file_id: int, user: dict) -> UploadedFile:
    item = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado.")
    if item.owner_id != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não possui acesso a este arquivo.")
    return item


@router.get("")
def list_files(
    purpose: str | None = Query(default=None, max_length=50),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    query = db.query(UploadedFile).filter(UploadedFile.owner_id == user["id"])
    if purpose:
        query = query.filter(UploadedFile.purpose == purpose)
    items = query.order_by(UploadedFile.created_at.desc(), UploadedFile.id.desc()).all()
    return success_response(data=[_serialize(item) for item in items], message="Arquivos retornados com sucesso.")


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    purpose: str = Form(default="general", min_length=1, max_length=50, pattern=r"^[a-z0-9_-]+$"),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    stored = await persist_upload(file)
    item = UploadedFile(owner_id=user["id"], purpose=purpose, **stored)
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except Exception:
        db.rollback()
        remove_stored_file(str(stored["storage_name"]))
        raise

    return success_response(
        data=_serialize(item),
        message="Arquivo enviado com sucesso.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/{file_id}")
def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    return success_response(
        data=_serialize(_owned_or_admin(db, file_id, user)),
        message="Metadata do arquivo retornada com sucesso.",
    )


@router.get("/{file_id}/content")
def get_file_content(
    file_id: int,
    download: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    item = _owned_or_admin(db, file_id, user)
    path = stored_path(item.storage_name)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Conteúdo físico do arquivo não está disponível.")

    disposition = "attachment" if download else "inline"
    encoded_name = quote(Path(item.original_name).name, safe="")
    return FileResponse(
        path=path,
        media_type=item.content_type,
        headers={
            "Content-Disposition": f"{disposition}; filename*=UTF-8''{encoded_name}",
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
        },
    )


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    item = _owned_or_admin(db, file_id, user)
    storage_name = item.storage_name
    db.delete(item)
    db.commit()
    remove_stored_file(storage_name)
    return success_response(data={"id": file_id}, message="Arquivo removido com sucesso.")
