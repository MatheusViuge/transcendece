#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MODEL="$ROOT/backend/backend/app/models/user.py"
SECURITY="$ROOT/backend/backend/app/core/security.py"
RBAC="$ROOT/backend/backend/app/core/rbac.py"
ADMIN="$ROOT/backend/backend/app/routers/admin.py"
CREATE_ADMIN="$ROOT/backend/backend/scripts/create_admin.py"
COURSES="$ROOT/backend/backend/app/routers/course.py"
API_KEY_AUTH="$ROOT/backend/backend/app/core/api_key_auth.py"
MIGRATION="$ROOT/backend/backend/alembic/versions_v2/0003_rbac_user_state.py"
FRONT_ACCESS="$ROOT/frontend/src/routes/access.ts"
FRONT_ADMIN="$ROOT/frontend/src/pages/Admin/Users.tsx"
FORBIDDEN="$ROOT/frontend/src/pages/Forbidden.tsx"
ROUTES="$ROOT/frontend/src/routes/AppRoutes.tsx"
DOCS="$ROOT/docs/evaluation/RBAC.md"

for file in "$MODEL" "$SECURITY" "$RBAC" "$ADMIN" "$CREATE_ADMIN" "$COURSES" "$API_KEY_AUTH" "$MIGRATION" "$FRONT_ACCESS" "$FRONT_ADMIN" "$FORBIDDEN" "$ROUTES" "$DOCS"; do
  test -f "$file"
done

grep -q 'ck_usuarios_tipo_usuario' "$MODEL"
grep -q 'is_active = Column' "$MODEL"
grep -q 'down_revision = "0002_public_api_keys"' "$MIGRATION"
grep -q 'def current_user' "$SECURITY"
grep -q 'getattr(user, "is_active", True)' "$SECURITY"
grep -q 'Conta desativada' "$SECURITY"
grep -q 'ROLE_PERMISSIONS' "$RBAC"
grep -q 'def require_permissions' "$RBAC"
grep -q 'Permission.ADMIN_USERS_READ' "$ADMIN"
grep -q 'Permission.ADMIN_ROLES_WRITE' "$ADMIN"
grep -q '/users/{user_id}/role' "$ADMIN"
grep -q '/users/{user_id}/status' "$ADMIN"
grep -q 'def create_first_admin' "$CREATE_ADMIN"
grep -q 'getpass(' "$CREATE_ADMIN"
grep -q 'Já existe uma conta admin' "$CREATE_ADMIN"
grep -q 'não promove usuários existentes' "$CREATE_ADMIN"
grep -q 'Permission.COURSE_STATS_OWN' "$COURSES"
grep -q 'Permission.COURSE_STATS_ANY' "$COURSES"
grep -q 'not owner.is_active' "$API_KEY_AUTH"
grep -q 'ROLE_NAV_LINKS' "$FRONT_ACCESS"
grep -q 'hasUiPermission' "$FRONT_ACCESS"
grep -q 'AdminUsers' "$ROUTES"
grep -q 'path="usuarios"' "$ROUTES"
grep -q '403' "$FORBIDDEN"
grep -q '/admin/users' "$FRONT_ADMIN"

# Public registration must not accept a writable role field.
if sed -n '/class UsuarioCriar/,/class UsuarioResponse/p' "$ROOT/backend/backend/app/schemas/user.py" | grep -q 'tipo_usuario'; then
  echo "UsuarioCriar must not expose tipo_usuario." >&2
  exit 1
fi

# Production bootstrap must never contain a hardcoded admin password.
if grep -Eq 'ADMIN_(PASSWORD|SENHA)[[:space:]]*=' "$CREATE_ADMIN"; then
  echo "create_admin.py must not contain a hardcoded admin password." >&2
  exit 1
fi

echo "RBAC structural/security check passed."
