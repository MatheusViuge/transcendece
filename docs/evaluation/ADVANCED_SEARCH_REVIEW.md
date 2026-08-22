# Advanced Search review checklist

Parent Epic: #25

## Automated

- [ ] backend regression passes
- [ ] `tests/test_advanced_search.py` passes
- [ ] `tests/test_seed_advanced_search.py` passes
- [ ] frontend lint passes
- [ ] frontend production build passes
- [ ] `sh scripts/search-check.sh` passes
- [ ] Docker images build in the serial backend → frontend → proxy order
- [ ] PostgreSQL becomes healthy and Alembic is at the single head
- [ ] manual Advanced Search seed runs twice on PostgreSQL without duplicate seed records
- [ ] exactly 30 seed courses and 12 seed users remain after the second run
- [ ] `/explorar` is served through HTTPS
- [ ] `/api/search/courses` is available through HTTPS/Nginx
- [ ] seeded `100%` course is searchable through HTTPS
- [ ] invalid `sort` returns HTTP 422 through HTTPS

## Manual setup

From the repository root with the production stack running:

```bash
docker compose exec backend python -m scripts.seed_advanced_search
```

All seed users use password `SearchSeed42!`.

## Manual UX review

- [ ] `/explorar` shows the populated catalog and more than one page
- [ ] searching `Python` returns matching persisted courses
- [ ] searching `100%` returns `APIs REST 100% Práticas`
- [ ] searching an instructor name returns that instructor's courses
- [ ] category filter works alone
- [ ] level filter works alone
- [ ] instructor filter works alone
- [ ] free/paid filter works alone
- [ ] multiple filters work together
- [ ] title sorting works asc/desc
- [ ] price sorting works asc/desc
- [ ] rating sorting works asc/desc, including courses with rating 0
- [ ] newest sorting changes the deterministic seeded creation-date order
- [ ] moving between pages preserves active filters
- [ ] refresh preserves state/results from the URL
- [ ] copied URL reproduces the same state in another tab
- [ ] browser Back/Forward restores previous search states
- [ ] loading/no-results/error states remain understandable
- [ ] Network shows `/api/search/courses`, not a full-catalog client-side filter
- [ ] console has no relevant application errors/warnings

## Module gate

- [ ] #46 validated
- [ ] #47 validated
- [ ] #48 validated
- [ ] #49 evidence recorded
- [ ] Epic #25 ready to merge/close
