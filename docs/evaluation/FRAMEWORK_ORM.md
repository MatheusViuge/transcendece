# Framework + ORM module evidence

This document is the review and evaluation evidence for Epic #22: **Frontend + Backend Framework (Major, 2 points) + ORM (Minor, 1 point)**.

## Claim status

The implementation is prepared for review on the Epic #22 integration branch. The three points should only be treated as integrated after the PR is reviewed, CI is green and the branch is merged. Final team attribution in the root README remains part of the project-wide contribution reconciliation (#16/#18/#19).

## Architecture

```text
Browser
  |
  | React Router + typed frontend services
  v
React application
  |
  | HTTPS /api/*
  v
Nginx reverse proxy
  |
  v
FastAPI router
  |
  v
Application service
  |
  v
Repository
  |
  | SQLAlchemy ORM
  v
PostgreSQL
  ^
  |
Alembic migrations
```

The framework and ORM claims are demonstrated by real application paths rather than isolated imports.

## Frontend framework evidence — React

- `frontend/src/App.tsx` is the small application composition root.
- `frontend/src/routes/AppRoutes.tsx` owns the React Router route tree.
- `frontend/src/routes/access.ts` centralizes typed role-to-route rules.
- `frontend/src/pages/Layout/PrivateRoute.tsx` composes authentication state with routing without replacing backend authorization.
- `frontend/src/services/api/` centralizes Axios access and uses the typed `ApiEnvelope<T>` contract.
- Context, hooks, pages and reusable components remain separated by responsibility.

Validation commands:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

## Backend framework evidence — FastAPI

- `backend/backend/app/main.py` exposes an application factory (`create_app`).
- `backend/backend/app/api/router.py` is the central router composition point.
- middleware, CORS and exception handlers are registered from `app/core`.
- the category vertical slice demonstrates thin HTTP routers delegating business rules to a service and persistence to a repository.
- OpenAPI is generated from the registered FastAPI routers and tested for representative application paths.

The category flow is intentionally used as a concrete architecture reference:

```text
HTTP /categories
  -> app/routers/category.py
  -> app/services/category_service.py
  -> app/repositories/category_repository.py
  -> SQLAlchemy Session
  -> relational database
```

## ORM evidence — SQLAlchemy + Alembic

The persisted domain uses SQLAlchemy models, relationships, foreign keys and database constraints. Representative protections include:

- unique user email;
- unique `(aluno_id, curso_id)` enrollment identity;
- composite `(matricula_id, aula_id)` progress primary key;
- explicit relationships between users, instructors, courses, modules, lessons, enrollments, progress, evaluations and certificates;
- cascade behavior on owned child collections;
- request-scoped SQLAlchemy sessions closed by `get_db`;
- a single active Alembic migration head used by clean deployment.

`tests/test_orm_architecture.py` validates mapper configuration, FK targets, important relationships and constraints, then performs create/read/update/delete through `CategoryRepository`.

`tests/test_framework_orm_integration.py` exercises the complete HTTP path for category CRUD, including FastAPI, service logic, repository access and SQLAlchemy persistence.

## Reproducible module gate

With the Compose stack running:

```bash
sh scripts/framework-orm-smoke.sh
```

The script validates:

1. React routes through HTTPS;
2. FastAPI health and category endpoints through `/api`;
3. a single Alembic head and database at head;
4. focused ORM architecture tests;
5. full FastAPI -> service -> repository -> SQLAlchemy CRUD integration.

The same smoke is executed by the repository CI deployment job so the module evidence stays coupled to the actual integration candidate.

## Evaluation demo

A short evaluator-facing sequence is:

1. show `App.tsx` and `routes/AppRoutes.tsx` to demonstrate React as the frontend framework;
2. navigate `/`, `/explorar`, login and one protected area;
3. show `create_app()` and `api/router.py` to demonstrate FastAPI composition;
4. show the category router/service/repository vertical slice;
5. show `Curso`, `Matricula` and `ProgressoAulas` relationships/constraints;
6. run `alembic heads` and `alembic current`;
7. run `sh scripts/framework-orm-smoke.sh`;
8. show the green CI run for the integration PR.

## Contributor evidence

The Epic #22 integration changes are authored through the project integration branch and linked PR. Final per-member attribution must be reconciled against merged Git/PR history before evaluation; this document does not invent ownership for work that is not yet verifiable.
