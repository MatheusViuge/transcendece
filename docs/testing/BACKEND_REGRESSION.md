# Backend mandatory regression

Run from `backend/backend`:

```bash
pytest
```

The test environment supplies a disposable SQLite database and a test-only JWT secret before application modules are imported. It does not read or modify a developer's production database.

## Automated mandatory coverage

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

## Optional modules are intentionally separate

Regression for optional features belongs to the QA issue of each module so the Mandatory Epic can close independently:

- Framework/ORM — #37
- Design System — #41
- PWA — #45
- Advanced Search — #49
- Public API — #55
- Advanced Permissions — #61
- File Upload — #65
- Standard User Management — #71
- User Interaction — #75
- WebSockets — #80
- Analytics — #86

Those suites must be added when their features are implemented; they are not represented here as skipped or fake-passing mandatory tests.

## Completion rule

Issue #88 is ready when the mandatory `pytest` suite passes in the target environment and the deployment-specific checks are executed through Issues #20 and #21.
