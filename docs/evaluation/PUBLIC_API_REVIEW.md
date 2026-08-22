# Public API — Reviewer Checklist

Parent Epic: #26.

## Automated

- [x] API key model stores hash, not usable secret
- [x] migration extends single Alembic head
- [x] create/list/revoke/rotate covered
- [x] missing, invalid and revoked key cases covered
- [x] read/write scopes covered
- [x] instructor ownership covered
- [x] GET/POST/PUT/DELETE covered
- [x] 5 endpoints covered
- [x] invalid payload returns 422
- [x] rate limit returns 429
- [x] second API key remains independent
- [x] external HTTPS smoke exercises the Public API through Nginx
- [x] consumer docs and curl examples present

## Manual spot-check

1. Start the clean stack and run the Advanced Search seed.
2. Login as `ana.ribeiro@seed.example.com` / `SearchSeed42!`.
3. Create a key with `courses:read` + `courses:write`.
4. Copy the secret; refresh/list keys and verify the secret is no longer shown.
5. Run the GET/POST/PUT/DELETE examples from `docs/PUBLIC_API.md`.
6. Revoke the key and confirm the next Public API request returns 401.
7. Open `/api/docs` and verify `Public API v1` + `X-API-Key`.
8. Optionally create a read-only key and verify POST returns 403.

## Merge gate

- automated workflow green;
- external examples match docs;
- no secrets committed/logged;
- reviewer confirms the v1 contract is understandable without reading source code.
