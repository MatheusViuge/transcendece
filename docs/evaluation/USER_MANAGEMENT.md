# Standard User Management — Evaluation Evidence

## Subject mapping

This implementation targets the **Major: Standard user management and authentication (2 pts)**:

- users can update their profile information;
- users can upload a custom avatar and receive a default avatar when none is selected;
- users can add/remove/list friends and see their online status;
- users have their own profile page and an authenticated public-profile view for other users.

## Backend

### Profile

- `GET /api/users/me` — private profile of the authenticated user.
- `PATCH /api/users/me` — updates only profile fields allowed by `UsuarioAtualizarParcial`.
- `GET /api/users/{user_id}` — public profile without email or birth date.
- `GET /api/users?q=...` — authenticated user discovery; returned payload is public-only.

Role, password and account-state changes are not accepted by the generic profile update endpoint.

### Avatar

The module reuses the File Upload & Management infrastructure.

1. Upload an image to `POST /api/files` with `purpose=avatar`.
2. Select it with `PUT /api/users/me/avatar/{file_id}`.
3. Remove it with `DELETE /api/users/me/avatar`; the default avatar is restored.
4. `GET /api/users/{user_id}/avatar` serves only the file explicitly selected as the public avatar.

Only PNG, JPEG and WebP can be selected as avatars. The upload must belong to the authenticated user. Replaced/removed avatar files are cleaned up. The default image is `frontend/public/default-avatar.svg`.

### Friends

Friendship is represented by a canonical unordered pair (`user_low_id`, `user_high_id`) with a database unique constraint and `user_low_id < user_high_id` check. This makes the relation symmetric and prevents duplicate inverse rows.

- `GET /api/users/friends`
- `POST /api/users/friends/{user_id}`
- `DELETE /api/users/friends/{user_id}`

Self-friendship is rejected and duplicate creation is protected both at application and database level.

### Online status

Presence is derived from `usuarios.last_seen_at` with a 90-second TTL instead of a permanent boolean. The authenticated frontend sends `POST /api/users/presence/heartbeat` every 30 seconds while a profile session is active.

This provides safe behavior for multiple browser tabs: any active tab refreshes the same timestamp, and an abrupt browser/network loss naturally expires after the TTL. Real-time WebSocket presence events remain a responsibility of the separate WebSocket module; this module does not claim WebSockets.

## Frontend

Routes:

- `/perfil` — own profile, editing, avatar management, friends list and user discovery.
- `/usuarios/:userId` — another user's profile with add/remove-friend action and status.

Both routes require authentication. All roles receive a `Perfil` navigation entry.

The profile UI includes loading/error/empty feedback, responsive layout, image upload progress, accessible labels and public/private field separation.

## Automated evidence

Backend integration tests: `backend/backend/tests/test_user_management.py`

They cover:

- profile update and persistence contract;
- rejection of protected profile fields;
- public-profile privacy;
- friend add/remove/list, self-friend and duplicate rejection;
- symmetric friendship consistency;
- heartbeat online state and timeout to offline;
- default avatar, custom avatar selection, cross-user rendering and reset to default.

Structural/security check: `scripts/user-management-check.sh`.

HTTPS multi-user smoke: `scripts/user-management-smoke.sh`. It runs in the deployment gate through the existing File Upload HTTPS step because avatar management deliberately integrates with the File Upload module.

## Manual Chrome demo

1. Start from a clean `docker compose up --build` environment.
2. Sign in as Alice and open `/perfil`.
3. Edit profile fields, refresh the page and confirm persistence.
4. Confirm the default avatar.
5. Upload a PNG/JPEG/WebP avatar, observe progress, select it and refresh.
6. Open another session as Camila.
7. Search for Alice, add her as a friend and confirm the relationship appears for both users.
8. Open Alice's public profile and confirm email/birth date are absent.
9. Keep Alice active and confirm online status; stop her heartbeat/session and wait past the 90-second TTL to demonstrate offline status.
10. Remove the friendship.
11. Remove Alice's avatar and confirm fallback to the default avatar.

## Scope boundary

The Standard User Management module provides profile, avatar, friendship and online-status functionality required by its subject entry. Instant push updates for presence/chat are intentionally not claimed here; those belong to the separate Real-time WebSocket module.
