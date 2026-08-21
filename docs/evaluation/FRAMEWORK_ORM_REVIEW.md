# Framework + ORM review checklist

Use this checklist while reviewing the Epic #22 integration PR.

## Frontend — Issue #34

- [ ] `frontend/src/App.tsx` is only the application composition root.
- [ ] `frontend/src/routes/AppRoutes.tsx` owns navigation structure.
- [ ] protected role routing uses typed rules from `frontend/src/routes/access.ts`.
- [ ] frontend API calls use typed `ApiEnvelope<T>` contracts.
- [ ] `npm run lint` passes.
- [ ] `npm run build` passes.

## Backend — Issue #35

- [ ] `create_app()` composes the FastAPI application.
- [ ] API routers are aggregated in `app/api/router.py`.
- [ ] CORS, JWT middleware and exception handlers are registered centrally.
- [ ] category endpoints are thin HTTP adapters over service/repository layers.
- [ ] OpenAPI exposes the expected application endpoints.
- [ ] no debug output remains in the category flow.

## ORM — Issue #36

- [ ] SQLAlchemy mapper configuration succeeds.
- [ ] core PK/FK relationships resolve to registered tables.
- [ ] enrollment uniqueness is enforced for `(aluno_id, curso_id)`.
- [ ] lesson progress has composite identity `(matricula_id, aula_id)`.
- [ ] repository CRUD persists and reloads real ORM entities.
- [ ] Alembic reports exactly one head and the database is at head.

## Integration — Issue #37

- [ ] backend `pytest` suite passes.
- [ ] frontend lint/build passes.
- [ ] clean Compose deployment passes.
- [ ] `sh scripts/framework-orm-smoke.sh` passes against the running stack.
- [ ] React routes are reachable through HTTPS.
- [ ] FastAPI endpoints are reachable through `/api`.
- [ ] focused HTTP CRUD covers FastAPI -> service -> repository -> SQLAlchemy.
- [ ] `docs/evaluation/FRAMEWORK_ORM.md` matches the implementation.

## Merge gate

The Epic may be considered technically complete when all automated checks above are green and the PR is reviewed. Final per-member attribution in the root README remains synchronized by the project-wide documentation/contribution issues before final evaluation.
