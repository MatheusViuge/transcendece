# Advanced Search — evaluation evidence

This document supports Epic #25 and child issues #46–#49.

## Scope

The public course catalog now uses a real server-side search endpoint backed by SQLAlchemy/PostgreSQL instead of downloading the full catalog and filtering it in the browser.

Endpoint:

```text
GET /search/courses
```

Supported parameters:

- `q`: text search over title, description, category, level and instructor name;
- `category_id`, `level_id`, `instructor_id`: combinable domain filters;
- `price`: `free` or `paid`;
- `sort`: `title`, `price`, `rating` or `newest`;
- `order`: `asc` or `desc`;
- `page`: 1-based page;
- `page_size`: 1–48, default 12.

## Backend behavior

The query joins courses with category, level, instructor/user and a rating aggregate subquery. Filtering and sorting are performed in SQL before pagination. Pagination is deterministic because every allowed primary sort is followed by `Curso.id` as a stable tie-breaker.

Text input escapes SQL LIKE wildcard characters (`%`, `_`, `\\`) before applying `ILIKE`, so user input is treated as literal search text rather than an uncontrolled wildcard expression.

Invalid enum values, non-positive IDs/pages and excessive page sizes are rejected by FastAPI validation with HTTP 422.

The response includes:

- result items from persisted data;
- `total`, `total_pages`, `has_previous`, `has_next`;
- category, level and instructor facets used by the public UI.

## Frontend behavior

`/explorar` uses the server endpoint directly and exposes:

- validated text search;
- category, level, instructor and price filters;
- configurable sorting and direction;
- reusable pagination;
- loading, error and no-results states.

The complete state is represented in `URLSearchParams` using `q`, `category`, `level`, `instructor`, `price`, `sort`, `order`, `page` and optional `page_size`. Invalid/empty URL values are normalized to safe defaults. Refresh and copied links therefore reproduce the same query, and browser back/forward navigation restores previous search states.

## Manual database seed

For manual evaluation, the backend includes an idempotent population script:

```text
backend/backend/scripts/seed_advanced_search.py
```

With the production stack already running and migrations applied, execute from the repository root:

```bash
docker compose exec backend python -m scripts.seed_advanced_search
```

Running the same command again is safe: seed users/courses are reused instead of duplicated, while the seed reviews are rebuilt deterministically.

The dataset contains:

- 4 instructor accounts;
- 8 student accounts;
- 30 courses across 5 categories and 3 levels;
- free and paid courses;
- different creation dates and ratings;
- courses without reviews (rating 0);
- accented content;
- a course named `APIs REST 100% Práticas` for literal wildcard testing;
- enough courses to force 3 pages with the UI default `page_size=12`.

All seed accounts use the password:

```text
SearchSeed42!
```

Instructor logins:

```text
ana.ribeiro@seed.example.com
bruno.costa@seed.example.com
carla.mendes@seed.example.com
diego.santos@seed.example.com
```

Student logins:

```text
alice.ferreira@seed.example.com
bernardo.lima@seed.example.com
camila.nunes@seed.example.com
eduardo.rocha@seed.example.com
fernanda.alves@seed.example.com
gabriel.barros@seed.example.com
helena.martins@seed.example.com
igor.pereira@seed.example.com
```

The seed is deliberately isolated with `@seed.example.com` accounts and a `[seed:advanced-search]` marker on seeded course/review descriptions, so it does not overwrite unrelated project records.

## Automated evidence

Backend regression includes `tests/test_advanced_search.py` and `tests/test_seed_advanced_search.py`, covering:

- combined text + category + level + price filters;
- ascending/descending allowlisted sorting;
- deterministic pagination without duplicate IDs between pages;
- accented text and literal `%` handling;
- invalid `page`, `page_size`, `sort` and `price` parameters;
- seed idempotency after two consecutive runs;
- exactly 30 seeded courses and 12 seeded users;
- searchability of the populated `100%` test course.

Run:

```bash
cd backend/backend
pytest tests/test_advanced_search.py tests/test_seed_advanced_search.py
```

Frontend/build structure:

```bash
cd frontend
npm ci
npm run lint
npm run build
cd ..
sh scripts/search-check.sh
```

The deployment workflow additionally runs the seed twice against the real PostgreSQL container, verifies the resulting counts, calls the search endpoint through the real HTTPS reverse proxy and confirms that an invalid sort returns 422.

## Evaluation demo

1. Start the production stack and run `docker compose exec backend python -m scripts.seed_advanced_search`.
2. Open `https://localhost/explorar`.
3. Search for `Python`, `100%`, an instructor name or a category.
4. Combine category/level/price filters.
5. Change sorting and direction, including rating and newest.
6. Move to another page and confirm filters remain in the URL.
7. Copy the URL, open it in another tab and confirm the same state/results.
8. Use browser Back/Forward and confirm previous search states return.
9. Show the Network request to `/api/search/courses` and its pagination metadata.
10. Demonstrate an invalid API parameter returning HTTP 422.

The root README remains the project skeleton until the final documentation/evaluation Epic; module evidence is kept here meanwhile.
