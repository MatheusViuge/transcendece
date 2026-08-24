# WebSockets / Realtime — evaluation evidence

This document is the technical evidence for Epic #31 (Major, 2 points).

## Module claim

The application uses an authenticated WebSocket channel for realtime chat events while keeping PostgreSQL and the REST API as the source of truth for persistence and historical pagination.

External endpoint:

`wss://<host>/api/ws/chat`

The JWT is **not** placed in the URL. After the WebSocket transport opens, the client immediately sends an authentication frame:

```json
{"type":"auth","token":"<access-token>"}
```

The server verifies signature/expiration and then resolves the current user, active status and role from the database before registering the socket. Invalid/inactive sessions are closed with WebSocket policy code `1008` and never join the broadcast registry.

## Architecture

### REST responsibilities

- create/get direct conversations;
- persist new messages in PostgreSQL;
- load the most recent history;
- paginate older history with `before_id`;
- recover gaps after reconnect with `after_id`.

### WebSocket responsibilities

- announce authenticated readiness with `realtime.ready`;
- fan out `chat.message.created` immediately after the PostgreSQL commit;
- keep connections alive with application-level `ping` / `realtime.pong`;
- deliver events only to the two users participating in the conversation.

The same message identifier is returned by REST and broadcast by WebSocket. The frontend merges/deduplicates by `message.id`, so the sender does not see a duplicate when the REST response and realtime event race each other.

## Backend

`backend/backend/app/realtime.py` owns the in-memory connection registry. A user can have multiple sockets (for example two tabs), and all sockets for each participant receive the event.

`backend/backend/app/routers/realtime.py` owns the WebSocket lifecycle and authentication handshake.

`backend/backend/app/routers/chat.py` publishes only **after** the database commit. Broadcasting uses the conversation's canonical `user_low_id` / `user_high_id`, preventing unrelated authenticated users from receiving the event.

The runtime explicitly includes the `websockets` package used by Uvicorn and by the WSS deployment smoke.

## Reconnect and gap recovery

The browser reconnects with exponential backoff capped at 10 seconds. After `realtime.ready`, every loaded conversation cache is reconciled with:

`GET /api/chat/conversations/{id}/messages?after_id=<last_known_message_id>`

The endpoint returns messages in ascending ID order. The client merges by ID, which makes recovery idempotent and prevents duplicate/reordered messages.

## Per-conversation cache

Chat state is held only in memory and indexed by `conversation_id`. Each entry tracks:

- loaded messages;
- `hasMore`;
- `nextBeforeId`;
- loading/loaded state.

Switching between conversations already visited reuses the in-memory entry instead of discarding the history and issuing a complete GET again.

Private chat content is not persisted to `localStorage`, `sessionStorage`, or PWA Cache Storage.

## Historical pagination and scroll behavior

The existing `before_id` cursor is preserved. An `IntersectionObserver` watches the top of the message viewport and automatically loads an older page when the user reaches it. The manual **Carregar anteriores** control remains as an accessibility/failure fallback.

Before older rows are prepended, the component records the scroll height/position and restores the visual offset after rendering, avoiding a jump in the viewport.

For new realtime messages, automatic following happens only while the user is already near the bottom. Reading older history is not interrupted by an incoming message.

## Session isolation / logout

The realtime effect is bound to `user.id`. A change in authenticated identity:

1. increments the request-generation boundary;
2. discards the per-conversation cache and selected conversation;
3. closes the previous WebSocket;
4. clears reconnect and keepalive timers;
5. ignores responses belonging to an older request generation;
6. starts the new identity from empty realtime state.

Unmounting the authenticated chat during logout closes an OPEN or CONNECTING socket with code `1000`.

## HTTPS / Nginx

The reverse proxy already forwards WebSocket Upgrade semantics under `/api/`:

- HTTP/1.1 upstream;
- `Upgrade` header;
- mapped `Connection: upgrade` header.

The deployment smoke opens real `wss://proxy/api/ws/chat` sockets from inside the Compose network, so the gate exercises TLS + Nginx + Uvicorn instead of testing only the ASGI endpoint directly.

## Automated evidence

`backend/backend/tests/test_websockets.py` covers:

- two authenticated clients receiving the same new message;
- a third authenticated client not receiving another conversation's event;
- invalid WebSocket authentication rejected with `1008`;
- disconnect plus `after_id` recovery of missed messages;
- mutually exclusive before/after cursor validation.

`scripts/websocket-check.sh` validates the structural/security contract.

`scripts/websocket-smoke.sh` validates the real Compose deployment with two WSS clients, realtime delivery, disconnect/gap recovery, reconnect and ping/pong.

## Evaluation walkthrough

1. Login as Alice and Camila in separate browser sessions.
2. Open the same direct conversation on both clients.
3. Show the `Tempo real conectado` state.
4. Send a message from Alice and show it appearing on Camila without refresh.
5. Send a response from Camila and show immediate delivery to Alice.
6. Open a third user and explain/verify that the broadcast is scoped to conversation participants.
7. Disconnect/reconnect one client, send messages during the gap, and show reconciliation without reload or duplicates.
8. Scroll upward far enough to load older pages and show that the viewport does not jump.
9. Logout and login as another account in the same browser; no prior chat cache is rendered.
10. Show the Nginx Upgrade configuration and automated WSS smoke if requested.
