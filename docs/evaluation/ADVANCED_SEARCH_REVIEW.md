# Advanced Search review checklist

Parent Epic: #25

## Automated — CI #100

- [x] backend regression passes
- [x] `tests/test_advanced_search.py` passes
- [x] `tests/test_seed_advanced_search.py` passes
- [x] frontend lint passes
- [x] frontend production build passes
- [x] `sh scripts/search-check.sh` passes
- [x] Docker images build in the serial backend → frontend → proxy order
- [x] PostgreSQL becomes healthy and Alembic is at the single head
- [x] manual Advanced Search seed runs twice on PostgreSQL without duplicate seed records
- [x] exactly 30 seed courses and 12 seed users remain after the second run
- [x] `/explorar` is served through HTTPS
- [x] `/api/search/courses` is available through HTTPS/Nginx
- [x] seeded `100%` course is searchable through HTTPS
- [x] invalid `sort` returns HTTP 422 through HTTPS

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

- [x] #46 automated implementation/evidence ready
- [x] #47 automated implementation/evidence ready
- [x] #48 automated implementation/evidence ready
- [x] #49 automated evidence recorded
- [ ] reviewer manual UX spot-check
- [ ] Epic #25 ready to merge/close
