# Public API — Evaluation Evidence

Parent Epic: #26 — Major, 2 points.

## Architecture

```text
External consumer
      |
      | X-API-Key
      v
/api/v1/public/*
      |
FastAPI Security(APIKeyHeader)
      |
PostgreSQL-backed key validation + fixed-window rate limit
      |
public schemas
      |
repository / SQLAlchemy
      |
PostgreSQL
```

The Public API remains inside the existing FastAPI modular monolith. It does not duplicate business data behind a separate gateway.

## Security properties

- full key secret is shown only on create/rotate;
- only SHA-256 hash + short prefix are persisted;
- secret comparison uses `hmac.compare_digest`;
- revoked keys stop working immediately;
- key management is JWT-protected and owner-scoped;
- `courses:write` is restricted to instructors;
- instructor ownership is derived from the API key, never from a client-controlled `instructor_id`;
- write operations use owner-filtered lookups;
- rate limiting is per key and stored in PostgreSQL with row locking;
- JWT and Public API authentication paths remain separate.

## Stable v1 surface

- `GET /v1/public/courses`
- `GET /v1/public/courses/{id}`
- `POST /v1/public/courses`
- `PUT /v1/public/courses/{id}`
- `DELETE /v1/public/courses/{id}`

Externally these are exposed under `/api/v1/public/...` by Nginx.

## Evidence

- migration `0002_public_api_keys`;
- integration suite `tests/test_public_api.py`;
- structural/security gate `scripts/public-api-check.sh`;
- external Docker/HTTPS smoke `scripts/public-api-smoke.sh`;
- consumer documentation `docs/PUBLIC_API.md`;
- OpenAPI `APIKeyHeader` security scheme.

The root README remains the subject-aligned skeleton from #116 and is intentionally finalized later in #16/#18/#33 with factual module contributors.
