from __future__ import annotations

from enum import Enum

from fastapi import Depends, HTTPException, status

from app.core.security import current_user


class Permission(str, Enum):
    ADMIN_USERS_READ = "admin:users:read"
    ADMIN_USERS_WRITE = "admin:users:write"
    ADMIN_ROLES_WRITE = "admin:roles:write"
    COURSE_CREATE = "courses:create"
    COURSE_UPDATE_OWN = "courses:update:own"
    COURSE_UPDATE_ANY = "courses:update:any"
    COURSE_DELETE_OWN = "courses:delete:own"
    COURSE_DELETE_ANY = "courses:delete:any"
    COURSE_STATS_OWN = "courses:stats:own"
    COURSE_STATS_ANY = "courses:stats:any"
    ENROLL_SELF = "enrollments:self"
    ENROLL_OWN_COURSE = "enrollments:own-course"
    ENROLL_ANY = "enrollments:any"
    REVIEW_CREATE = "reviews:create"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "aluno": frozenset({
        Permission.ENROLL_SELF,
        Permission.REVIEW_CREATE,
    }),
    "instrutor": frozenset({
        Permission.COURSE_CREATE,
        Permission.COURSE_UPDATE_OWN,
        Permission.COURSE_DELETE_OWN,
        Permission.COURSE_STATS_OWN,
        Permission.ENROLL_OWN_COURSE,
    }),
    "admin": frozenset(Permission),
}


def has_permission(role: str, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def require_permissions(*permissions: Permission):
    """FastAPI dependency que exige todas as permissões informadas.

    O usuário vem de `current_user`, que sempre consulta a role persistida no
    banco. Portanto uma mudança de role entra em vigor no request seguinte sem
    depender de reemissão do JWT.
    """

    def dependency(usuario: dict = Depends(current_user)) -> dict:
        missing = [permission.value for permission in permissions if not has_permission(usuario["role"], permission)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta operação.",
            )
        return usuario

    return dependency
