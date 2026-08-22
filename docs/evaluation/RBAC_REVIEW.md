# Advanced Permissions / RBAC — Reviewer Checklist

Parent Epic: #27.

## Seed

```bash
docker compose exec backend python -m scripts.seed_rbac
```

Admin manual:

- email: `admin.rbac@seed.example.com`
- password: `SearchSeed42!`

The Advanced Search instructors/students remain available with the same seed password.

## Automated evidence

- [x] accepted roles are constrained in the database
- [x] current role and active state are loaded from PostgreSQL on protected requests
- [x] public registration cannot choose a privileged role
- [x] admin CRUD/user filtering exists
- [x] role changes are admin-only
- [x] self-lockout and last-admin lockout are blocked
- [x] inactive accounts invalidate existing sessions
- [x] instructor course statistics enforce ownership
- [x] Public API keys stop authenticating for inactive owners
- [x] frontend role routing and explicit 403 state are present
- [x] admin panel is responsive and consumes real API data

## Manual demo

1. Login as `admin.rbac@seed.example.com`.
2. Open `/admin/usuarios` and search/filter the seeded users.
3. Create a temporary student, edit its name/email and refresh the page.
4. Change the temporary user from student to instructor and verify the new role persists.
5. Disable that user and verify login is denied.
6. Try to change the admin's own role or disable the current admin and verify the operation is rejected.
7. Login as a student and open `/admin/usuarios` directly; verify the explicit 403 UI and that direct API access also returns 403.
8. Login as Ana and verify her course statistics work; use another instructor against Ana's course ID and verify 403.
9. Return to an already-open session after changing its role from the admin panel and refocus/reload it; verify the frontend refreshes the current role.
10. Inspect Network/response payloads and confirm no password hash/API secret is returned by admin user endpoints.

## Merge gate

- full Mandatory Gate green;
- PostgreSQL migration has a single Alembic head;
- backend authorization tests green;
- HTTPS RBAC smoke green;
- manual admin and forbidden-route flow understandable without reading source code.
