# Advanced Permissions / RBAC — Evaluation Evidence

Parent Epic: #27 — Major, 2 points.

## Architecture

```text
JWT identity
    |
    v
current_user()
    |
    | always reloads user from PostgreSQL
    v
active account + current persisted role
    |
    v
permission matrix (app/core/rbac.py)
    |
    +--> admin CRUD / role management
    +--> course ownership policies
    +--> enrollment/review policies
    +--> frontend role-aware routing
```

The JWT deliberately does **not** act as the source of truth for roles. A role change or account deactivation takes effect on the next protected request without waiting for token expiration.

## Domain roles

| Role | Core permissions |
| --- | --- |
| `aluno` | own enrollments/progress, create reviews for enrolled courses |
| `instrutor` | create courses, update/delete/view statistics of own courses, manage enrollments of own courses |
| `admin` | administrative user/role CRUD and unrestricted administrative course permissions |

The database enforces the accepted role set through `ck_usuarios_tipo_usuario`.

## Administrative surface

Backend endpoints under `/admin` are permission-protected:

- `GET /admin/users` — paginated list with query, role and active-state filters;
- `POST /admin/users` — administrative creation;
- `GET /admin/users/{id}` — detail without password/secrets;
- `PATCH /admin/users/{id}` — editable profile fields;
- `PATCH /admin/users/{id}/role` — role transitions;
- `PATCH /admin/users/{id}/status` — activate/deactivate;
- `DELETE /admin/users/{id}` — safe soft-deactivation preserving historical relationships;
- `GET /admin/permissions` — demonstrable permission matrix;
- `GET /admin/specialties` — valid instructor-specialty choices.

Frontend route `/admin/usuarios` provides the demonstrable admin panel with search/filtering, pagination, create/edit, role changes and activation state.

## Production first-admin bootstrap

Public registration intentionally always creates `aluno`, so a fresh production installation needs one out-of-band bootstrap step before the RBAC admin surface can be used.

Run inside the backend container:

```bash
docker compose exec backend python -m scripts.create_admin
```

The command asks for name, surname, email, birth date, password and password confirmation. Password input uses `getpass`, so it is not echoed to the terminal and no production credential is hardcoded in the repository.

Bootstrap safety rules:

- the command works only while no `admin` record exists;
- inactive admin records still count, preventing silent creation of a second bootstrap admin;
- an email already owned by any account is rejected instead of silently promoting that account;
- the same `AdminUserCreate` validation rules are reused for email, password strength and birth date;
- the password is persisted only through the application's password hashing function;
- after the first admin exists, additional admins must be managed through `/admin/usuarios` / `/admin/users`.

The deterministic `python -m scripts.seed_rbac` command remains development/evaluation-only and is not the production bootstrap mechanism.

## Privilege-escalation protections

- public registration always creates `aluno`;
- public profile payloads contain no writable role field;
- role changes require the admin permission dependency;
- roles are reloaded from PostgreSQL for every protected request;
- inactive users are rejected even with a still-valid JWT;
- admins cannot change their own role or disable themselves;
- the last active admin cannot be demoted/deactivated;
- instructor demotion is blocked while courses still depend on that instructor;
- course update/delete/statistics enforce owner-or-admin permissions;
- an instructor cannot obtain another instructor's protected data by changing a URL ID;
- API keys become invalid when their owner is inactive; Public API write also checks the owner's current instructor role.

## Authentication vs authorization

- `401` means authentication material is absent/invalid/expired;
- `403` means an authenticated identity exists but current role/status/ownership does not permit the operation;
- `409` is used for administrative state transitions that would create an invalid system state (self-lockout, last-admin lockout, instructor with dependent courses).

## Evidence

- migration `0003_rbac_user_state`;
- central authorization in `app/core/security.py` and `app/core/rbac.py`;
- admin service/router in `app/services/admin_user_service.py` and `app/routers/admin.py`;
- authorization regression `tests/test_rbac.py`;
- production first-admin bootstrap `python -m scripts.create_admin`;
- bootstrap regression `tests/test_create_admin.py`;
- deterministic development/evaluation seed `python -m scripts.seed_rbac`;
- frontend role map in `frontend/src/routes/access.ts`;
- explicit 403 UX in `frontend/src/pages/Forbidden.tsx`;
- admin panel in `frontend/src/pages/Admin/Users.tsx`;
- structural check `scripts/rbac-check.sh`;
- Docker/PostgreSQL/HTTPS smoke in the Mandatory Gate.

The root README remains the subject-aligned skeleton and is intentionally finalized in #16/#18/#33 with factual contributors and final module status.
