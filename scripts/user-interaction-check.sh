#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

require_file() {
  test -f "$1" || { echo "Missing required User Interaction file: $1" >&2; exit 1; }
}

require_pattern() {
  pattern=$1
  file=$2
  grep -Eq "$pattern" "$file" || { echo "Missing User Interaction pattern '$pattern' in $file" >&2; exit 1; }
}

require_file backend/backend/app/models/chat.py
require_file backend/backend/app/routers/chat.py
require_file backend/backend/app/schemas/chat.py
require_file backend/backend/alembic/versions_v2/0006_user_interaction.py
require_file backend/backend/tests/test_user_interaction.py
require_file frontend/src/pages/Chat/index.tsx
require_file scripts/user-interaction-smoke.sh

require_pattern 'UniqueConstraint\("user_low_id", "user_high_id"' backend/backend/app/models/chat.py
require_pattern 'CheckConstraint\("user_low_id < user_high_id"' backend/backend/app/models/chat.py
require_pattern 'length\(content\) BETWEEN 1 AND 2000' backend/backend/app/models/chat.py
require_pattern '@router.post\("/conversations"\)' backend/backend/app/routers/chat.py
require_pattern '@router.get\("/conversations"\)' backend/backend/app/routers/chat.py
require_pattern '@router.get\("/conversations/\{conversation_id\}/messages"\)' backend/backend/app/routers/chat.py
require_pattern '@router.post\("/conversations/\{conversation_id\}/messages"' backend/backend/app/routers/chat.py
require_pattern '_participant_conversation' backend/backend/app/routers/chat.py
require_pattern 'before_id' backend/backend/app/routers/chat.py
require_pattern 'chat.message.created' backend/backend/app/routers/chat.py
require_pattern 'maxLength=\{2000\}' frontend/src/pages/Chat/index.tsx
require_pattern 'Carregar anteriores' frontend/src/pages/Chat/index.tsx
require_pattern '/chat\?user=' frontend/src/pages/Profile/index.tsx
require_pattern 'path="/chat"' frontend/src/routes/AppRoutes.tsx

printf '%s\n' 'User Interaction structural/security check passed.'
