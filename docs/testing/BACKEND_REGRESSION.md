# Backend regression matrix

The backend regression command is executed from `backend/backend`:

```bash
pytest
```

The test environment supplies a disposable SQLite database and a test-only JWT secret before application modules are imported. It does not read or modify a developer's production database.

## Mandatory coverage available now

| Area | Automated coverage |
| --- | --- |
| Password storage | PBKDF2 hash is not plain text; random salts produce different hashes; wrong password and invalid hash are rejected |
| Input validation | unknown fields, role mass assignment, future birth date, weak password and forged review IDs are rejected |
| JWT | valid token, expired token, wrong signature, invalid type, current database role and 401/403 semantics |
| Auth API | signup, duplicate email, login, generic invalid credentials, `/me`, missing/invalid token, public role escalation and admin-route denial |
| Multi-user constraints | unique enrollment per student/course and composite lesson-progress key |
| Health/auth middleware | `/status` and CORS preflight remain public |

## Manual/integration checks that remain mandatory

The unit/in-process suite does not replace deployment validation. The following still require the Docker/HTTPS environment:

- [ ] Alembic migration against a fresh PostgreSQL database;
- [ ] HTTPS reverse proxy and HTTP redirect;
- [ ] Chrome Console/Network validation;
- [ ] two independent browser sessions;
- [ ] concurrent enrollment smoke (`scripts/concurrency_smoke.py`);
- [ ] persistence across container restart;
- [ ] clean-clone smoke (`scripts/clean-install-smoke.sh`).

## Optional-module regression gates

Issue #88 was intentionally written to eventually cover the complete 19-point product. Those tests must be added when the corresponding modules are implemented; they cannot be truthfully marked as passing while the features do not exist.

### Public API

When Epic #26 is implemented, add automated tests for:

- [ ] API key valid/invalid/revoked;
- [ ] rate limiting and 429 response;
- [ ] public endpoint smoke coverage.

### Advanced Permissions

When Epic #27 is implemented, expand tests for:

- [ ] user CRUD;
- [ ] role management;
- [ ] ownership and IDOR;
- [ ] privilege escalation.

### File Upload

When Epic #28 is implemented, add:

- [ ] valid upload;
- [ ] invalid type/size/content;
- [ ] ownership/download/delete;
- [ ] storage cleanup.

### User Management / Interaction

When Epics #29–#30 are implemented, add:

- [ ] profile update;
- [ ] avatar lifecycle;
- [ ] friends add/remove/list;
- [ ] conversations/messages and third-user denial.

### Realtime

When Epic #31 is implemented, add:

- [ ] authenticated WebSocket connection;
- [ ] invalid connection rejection;
- [ ] scoped broadcasting;
- [ ] reconnect/disconnect behavior.

### Analytics

When Epic #32 is implemented, add:

- [ ] KPIs and chart datasets;
- [ ] date range/filter behavior;
- [ ] permissions;
- [ ] CSV/PDF exports;
- [ ] realtime invalidation/update smoke.

## Completion rule

For the Mandatory Compliance Epic, the mandatory test group plus the clean-install/multi-user manual checks are the relevant gate. The broader Issue #88 should remain open as a cross-project regression tracker until the selected optional modules have added their test groups.
