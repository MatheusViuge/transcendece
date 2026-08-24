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

### Public Friend Code

Each user owns a random, unique `friend_code` formatted as `ABCDE-FGHIJ`. The value is generated independently from email, database ID or other personal fields, and the database enforces uniqueness.

User discovery accepts an exact Friend Code with or without the visual hyphen. Normal discovery remains available by name/surname; email is not used by the social search path.

### Avatar

The module reuses the File Upload & Management infrastructure.

1. Upload an image to `POST /api/files` with `purpose=avatar`.
2. Select it with `PUT /api/users/me/avatar/{file_id}`.
3. Remove it with `DELETE /api/users/me/avatar`; the default avatar is restored.
4. `GET /api/users/{user_id}/avatar` serves only the file explicitly selected as the public avatar.

Only PNG, JPEG and WebP can be selected as avatars. The upload must belong to the authenticated user. Replaced/removed avatar files are cleaned up. The default image is `frontend/public/default-avatar.svg`.

### Friends and consent

Accepted friendship remains represented by a canonical unordered pair (`user_low_id`, `user_high_id`) with a database unique constraint and `user_low_id < user_high_id` check. The relation is symmetric and duplicate inverse rows are impossible.

Friendship creation is no longer unilateral. A pending request is represented by `FriendRequest`, also canonical per pair, while `requester_id` records who initiated it.

- `GET /api/users/friends` — accepted friends only.
- `GET /api/users/friend-requests` — incoming/outgoing pending requests.
- `POST /api/users/friend-requests/{user_id}` — send a request.
- `POST /api/users/friend-requests/{user_id}/accept` — recipient accepts a request sent by `user_id`.
- `DELETE /api/users/friend-requests/{user_id}` — recipient declines or requester cancels.
- `DELETE /api/users/friends/{user_id}` — remove an accepted friendship.

Self-requests, duplicate requests, inverse simultaneous requests and creation of a request for an existing friendship are rejected. There is deliberately no `POST /friends/{user_id}` shortcut capable of creating an accepted friendship without consent.

Existing accepted friendships are preserved by migration `0007_friendship_privacy`.

### Online status and privacy

Presence is derived from `usuarios.last_seen_at` with a 90-second TTL instead of a permanent boolean. The authenticated frontend sends `POST /api/users/presence/heartbeat` every 30 seconds while a profile session is active.

Presence is treated as relationship-scoped information:

- the user can see their own presence state;
- accepted friends can see each other's online/offline state;
- search results, pending requests and public profiles of non-friends return `online: null`;
- chat participant payloads also return `online: null` when the participants are not accepted friends.

This prevents a user from converting public discovery into unilateral presence tracking. Real-time WebSocket presence events remain a responsibility of the separate WebSocket module and must preserve the same authorization rule.

## Frontend

Routes:

- `/perfil` — own profile, editing, avatar management, Friend Code, accepted friends, pending requests and user discovery.
- `/usuarios/:userId` — another user's profile with request/accept/decline/cancel/remove controls according to relationship state.

Both routes require authentication. All roles receive a `Perfil` navigation entry.

The profile UI includes loading/error/empty feedback, responsive layout, image upload progress, accessible labels and public/private field separation. Non-friend presence is rendered as **Presença privada**, never as a fabricated offline state.

## Automated evidence

Backend integration tests: `backend/backend/tests/test_user_management.py`

They cover:

- profile update and persistence contract;
- rejection of protected profile fields;
- public-profile privacy;
- Friend Code format/uniqueness and exact-code discovery;
- pending request send/list/accept/decline/cancel behavior;
- prevention of unilateral friendship creation;
- symmetric accepted-friendship consistency and removal;
- presence hidden before acceptance and visible after acceptance;
- heartbeat online state and timeout to offline;
- default avatar, custom avatar selection, cross-user rendering and reset to default.

Structural/security check: `scripts/user-management-check.sh`.

HTTPS multi-user smoke: `scripts/user-management-smoke.sh`. It demonstrates discovery by Friend Code, hidden pre-consent presence, request/accept, visible friend presence, avatar behavior and removal returning presence to private.

## Manual Chrome demo

1. Start from a clean `docker compose up --build` environment.
2. Sign in as Alice and open `/perfil`; copy her Friend Code.
3. Open another session as Camila and search Alice by the Friend Code.
4. Confirm Alice's presence is shown as private before friendship.
5. Send a friendship request and confirm neither side is yet listed as an accepted friend.
6. In Alice's session, verify the incoming request and accept it.
7. Confirm the relationship appears for both users and online/offline presence is now visible.
8. Remove the friendship and confirm presence becomes private again.
9. Exercise decline and cancel paths with another seeded user.
10. Edit profile fields and confirm persistence after refresh.
11. Upload/remove an avatar and confirm public rendering/default fallback.
12. Confirm public profiles do not expose email or birth date.
13. Confirm the browser console has no relevant warnings/errors.

## Scope boundary

The consent/Friend Code changes are a privacy hardening hotfix around the existing Standard User Management behavior; they do not claim additional subject points. Blocking, followers, close-friends groups and push notifications are intentionally outside this hotfix.
