# User Interaction — Evaluation Evidence

## Subject mapping

This Epic targets the **User Interaction** Major module (2 points):

- basic chat between users;
- profile system integrated into interactions;
- friends can be added, removed and listed as part of the social flow.

The implementation intentionally keeps real-time delivery out of this module. Persistent REST chat is complete here; authenticated WebSocket delivery/reconnect/broadcasting belongs to Epic #31.

## Architecture

### Direct conversations

A `conversation` represents exactly two users. The database stores the participant pair canonically as `user_low_id < user_high_id` and enforces a unique constraint on that pair. This prevents duplicate Alice↔Camila and Camila↔Alice conversations even under concurrent creation attempts.

### Persistent messages

`chat_messages` stores:

- conversation id;
- sender id;
- normalized message content;
- creation timestamp.

Message content is trimmed and limited to 1–2000 characters in the API schema and database constraint.

### Authorization

Every conversation-history or send operation resolves the authenticated user through the existing JWT/RBAC stack and then scopes the conversation query to that user. A non-participant receives `404`, avoiding both data disclosure and confirmation that a private conversation exists.

### Pagination

History uses cursor pagination with `before_id`. The API reads messages newest-first for an efficient indexed query, returns the selected page in chronological order, and provides `next_before_id` when older messages exist.

### WebSocket readiness

Message responses expose `event: "chat.message.created"`. Epic #31 can publish the same payload over authenticated WebSockets without changing persistence or the frontend message contract.

### Session/logout boundary

The authenticated Navbar exposes a visible **Sair** action. It stays visually secondary by default and only gains destructive emphasis on pointer hover or keyboard focus so logout remains discoverable without competing with the primary navigation.

Logout removes the authentication token from the browser's known auth storage locations, clears the current user from `UserContext`, and redirects to `/login`. The implementation intentionally does not call `localStorage.clear()` or clear the PWA Cache Storage because those stores can contain non-user technical state.

In the current Epic, chat history is component-local state; leaving the authenticated route unmounts the chat and destroys that in-memory state. Epic #31 must preserve this session boundary when introducing a conversation cache and WebSocket state: cache/socket state from one identity must never survive into another authenticated identity.

## Endpoints

- `POST /api/chat/conversations` — create or return a direct conversation by `recipient_id`;
- `GET /api/chat/conversations` — list the authenticated user's conversations;
- `GET /api/chat/conversations/{id}/messages` — paginated private history;
- `POST /api/chat/conversations/{id}/messages` — persist a new message.

## Frontend flow

- `/chat` is authenticated-only and available to aluno, instrutor and admin navigation;
- conversations show participant avatar, online/offline status and last message;
- selecting a conversation loads its persisted history;
- older history is loaded through the cursor endpoint;
- the composer prevents empty sends and limits input to 2000 characters;
- sending is disabled while a request is pending to reduce accidental duplicates;
- a recoverable error is shown if sending fails;
- the conversation header opens the participant profile;
- another user's profile exposes **Conversar**;
- each friend entry exposes **Chat**;
- friends can still be added/removed through the profile flow from Epic #29;
- authenticated navigation always exposes **Sair** outside the horizontally scrollable role-link area;
- logout clears the auth token/current user and returns the browser to `/login`.

## Automated coverage

`backend/backend/tests/test_user_interaction.py` covers:

- canonical/idempotent conversation creation;
- self-conversation rejection;
- third-user read/write isolation;
- persistent bidirectional messaging;
- stable cursor pagination;
- conversation list/last-message payload;
- empty and oversized message rejection;
- persisted rows in the database.

`scripts/user-interaction-check.sh` guards the required models/routes/migration/frontend integration, including the logout action and auth-storage cleanup contract.

`scripts/user-interaction-smoke.sh` executes the real HTTPS/PostgreSQL/Docker flow with seeded users Alice, Camila and Bernardo. It creates a conversation, sends messages in both directions, rejects Bernardo as a third-party intruder, validates pagination/listing, restarts the backend container, then confirms the messages still exist.

## Manual Chrome walkthrough

1. Start from a clean deployment and run the advanced-search seed.
2. Open two Chrome sessions/profiles.
3. Log in as `alice.ferreira@seed.example.com` and `camila.nunes@seed.example.com` using the documented seed password.
4. From Alice, open Camila's profile and click **Conversar**.
5. Send a message; verify it appears with timestamp and survives page refresh.
6. In Camila's session, open **Chat**, select Alice and click **Atualizar**; reply.
7. In Alice's session, click **Atualizar** and verify the reply.
8. Open the participant profile from the chat header.
9. Add/remove the user as a friend and verify the social state after refresh.
10. Generate enough messages to use **Carregar anteriores** and verify order remains chronological.
11. Verify **Sair** remains visible in the authenticated Navbar, appears muted at rest, and gains the danger highlight on hover/focus.
12. Click **Sair**; verify the app redirects to `/login`, the authenticated Navbar disappears, and the `token` key is absent from `localStorage` and `sessionStorage`.
13. Log in as a different seeded user and verify no previous authenticated chat UI/state is visible before that user's own data is requested.
14. Confirm the browser console has no relevant JavaScript errors.
15. Repeat the layout check at mobile and desktop widths.

## Expected future change in Epic #31

The **Atualizar** action is deliberately explicit in this Epic. Epic #31 will add authenticated WebSocket lifecycle, scoped room broadcasting, reconnect/cleanup and immediate message/presence updates. REST remains the durable persistence and history fallback. Any cache introduced there must be scoped to the authenticated `user.id` and cleared together with the socket/realtime state on logout or identity change.
