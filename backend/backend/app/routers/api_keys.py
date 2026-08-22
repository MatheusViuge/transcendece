from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.core.security import allowed_roles
from app.database import get_db
from app.models.user import Usuario
from app.schemas.api_key import ApiKeyCreateRequest, ApiKeyCreated, ApiKeyInfo
from app.services.api_key_service import (
    deserialize_scopes,
    issue_api_key,
    list_api_keys,
    revoke_api_key,
    rotate_api_key,
)

# Keep the internal path distinct from FastAPI's root_path="/api".  Nginx
# exposes this router externally as /api/keys while proxying /keys to Uvicorn.
router = APIRouter(prefix="/keys", tags=["API Keys"])


def _owner(db: Session, user_id: int) -> Usuario:
    return db.query(Usuario).filter(Usuario.id == user_id).one()


def _info(api_key) -> ApiKeyInfo:
    return ApiKeyInfo(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.prefix,
        scopes=sorted(deserialize_scopes(api_key.scopes)),
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        revoked_at=api_key.revoked_at,
        active=api_key.revoked_at is None,
    )


def _created(api_key, secret: str) -> ApiKeyCreated:
    return ApiKeyCreated(**_info(api_key).model_dump(), secret=secret)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    current=Depends(allowed_roles()),
):
    api_key, secret = issue_api_key(
        db,
        owner=_owner(db, current["id"]),
        name=payload.name,
        requested_scopes=payload.scopes,
    )
    return success_response(
        data=_created(api_key, secret),
        message="API key criada. O secret completo não poderá ser consultado novamente.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("")
def get_api_keys(
    db: Session = Depends(get_db),
    current=Depends(allowed_roles()),
):
    keys = list_api_keys(db, owner_id=current["id"])
    return success_response(
        data=[_info(api_key) for api_key in keys],
        message="API keys do usuário retornadas com sucesso.",
    )


@router.delete("/{api_key_id}")
def revoke_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current=Depends(allowed_roles()),
):
    api_key = revoke_api_key(db, owner_id=current["id"], api_key_id=api_key_id)
    return success_response(data=_info(api_key), message="API key revogada com sucesso.")


@router.post("/{api_key_id}/rotate", status_code=status.HTTP_201_CREATED)
def rotate_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current=Depends(allowed_roles()),
):
    replacement, secret = rotate_api_key(
        db,
        owner=_owner(db, current["id"]),
        api_key_id=api_key_id,
    )
    return success_response(
        data=_created(replacement, secret),
        message="API key rotacionada. A key anterior foi revogada.",
        status_code=status.HTTP_201_CREATED,
    )
