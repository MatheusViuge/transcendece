# Database migrations

Alembic is the only supported mechanism for creating or changing the application schema.

## Active migration line

The active revision directory is:

```text
backend/alembic/versions_v2/
```

The older `backend/alembic/versions/` directory is retained only as historical development material and is not part of the clean deployment migration graph.

## Apply migrations

From the backend application directory (`backend/backend` when running on the host, `/app` in the container):

```bash
alembic upgrade head
```

The production backend container runs this command automatically before Uvicorn starts.

## Inspect state

```bash
alembic current
alembic heads
alembic history
```

A clean evaluation database must report a single head.

## Create a new migration

After changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the schema change"
```

Always review the generated migration before committing it. Autogenerate is a helper, not a substitute for schema review.

## Roll back one revision

```bash
alembic downgrade -1
```

Do not rewrite an already shared migration to represent a new schema change; add a new revision instead.

## Clean-database validation

The final validation path is:

```bash
docker compose down -v
docker compose up --build
```

The PostgreSQL volume starts empty, Alembic upgrades it to `head`, and the API must start without `Base.metadata.create_all()` or manual SQL steps.
