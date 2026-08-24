#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
USER_MODEL="$ROOT/backend/backend/app/models/user.py"
FRIEND_MODEL="$ROOT/backend/backend/app/models/friendship.py"
ROUTER="$ROOT/backend/backend/app/routers/users.py"
MIGRATION="$ROOT/backend/backend/alembic/versions_v2/0005_user_management.py"
PRIVACY_MIGRATION="$ROOT/backend/backend/alembic/versions_v2/0007_friendship_privacy.py"
TESTS="$ROOT/backend/backend/tests/test_user_management.py"
PROFILE="$ROOT/frontend/src/pages/Profile/index.tsx"
ROUTES="$ROOT/frontend/src/routes/AppRoutes.tsx"
ACCESS="$ROOT/frontend/src/routes/access.ts"
PRIVATE_ROUTE="$ROOT/frontend/src/pages/Layout/PrivateRoute.tsx"
DEFAULT_AVATAR="$ROOT/frontend/public/default-avatar.svg"
FRIEND_CODE_SERVICE="$ROOT/backend/backend/app/services/friend_code.py"

for file in "$USER_MODEL" "$FRIEND_MODEL" "$ROUTER" "$MIGRATION" "$PRIVACY_MIGRATION" "$TESTS" "$PROFILE" "$ROUTES" "$ACCESS" "$PRIVATE_ROUTE" "$DEFAULT_AVATAR" "$FRIEND_CODE_SERVICE"; do
  test -f "$file"
done

grep -q 'down_revision = "0004_file_upload"' "$MIGRATION"
grep -q 'down_revision = "0006_user_interaction"' "$PRIVACY_MIGRATION"
grep -q 'avatar_file_id' "$USER_MODEL"
grep -q 'last_seen_at' "$USER_MODEL"
grep -q 'friend_code' "$USER_MODEL"
grep -q 'uq_friendships_pair' "$FRIEND_MODEL"
grep -q 'ck_friendships_order' "$FRIEND_MODEL"
grep -q 'class FriendRequest' "$FRIEND_MODEL"
grep -q 'uq_friend_requests_pair' "$FRIEND_MODEL"
grep -q '@router.patch("/me")' "$ROUTER"
grep -q '@router.post("/friend-requests/{user_id}"' "$ROUTER"
grep -q '@router.post("/friend-requests/{user_id}/accept"' "$ROUTER"
grep -q '@router.delete("/friend-requests/{user_id}"' "$ROUTER"
grep -q '@router.delete("/friends/{user_id}"' "$ROUTER"
grep -q '@router.get("/friends")' "$ROUTER"
grep -q '@router.get("/friend-requests")' "$ROUTER"
grep -q '@router.post("/presence/heartbeat")' "$ROUTER"
grep -q 'PRESENCE_TTL' "$ROUTER"
grep -q 'normalize_friend_code' "$ROUTER"
grep -q 'online=None' "$ROUTER"
grep -q 'purpose != "avatar"' "$ROUTER"
grep -q 'IMAGE_TYPES' "$ROUTER"
grep -q 'DEFAULT_AVATAR_URL' "$ROUTER"
grep -q 'onUploadProgress' "$PROFILE"
grep -q 'Adicionar amigo' "$PROFILE"
grep -q 'Aceitar' "$PROFILE"
grep -q 'Recusar' "$PROFILE"
grep -q 'Friend Code' "$PROFILE"
grep -q 'Presença privada' "$PROFILE"
grep -q 'path="/perfil"' "$ROUTES"
grep -q 'path="/usuarios/:userId"' "$ROUTES"
grep -q 'isAuthenticatedOnlyPath' "$PRIVATE_ROUTE"
grep -q 'Perfil.*to: "/perfil"' "$ACCESS"

# No route may recreate the previous unilateral friendship shortcut.
! grep -q '@router.post("/friends/{user_id}"' "$ROUTER"

# Protected profile updates must not accept role/account-state/password fields.
! grep -q 'tipo_usuario.*UsuarioAtualizarParcial' "$ROOT/backend/backend/app/schemas/user.py"
! grep -q 'senha.*UsuarioAtualizarParcial' "$ROOT/backend/backend/app/schemas/user.py"

# Presence must be derived from a timestamp/TTL, not a permanent online boolean.
! grep -q 'is_online = Column' "$USER_MODEL"

# Friend codes must be random public identifiers, never hashes of email/internal IDs.
! grep -q 'email' "$FRIEND_CODE_SERVICE"
! grep -q 'user_id' "$FRIEND_CODE_SERVICE"

echo "Standard User Management friendship-consent/privacy check passed."
