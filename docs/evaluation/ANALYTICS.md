# Advanced Analytics Dashboard — evaluation evidence

This document is the technical evidence for Epic #32 (Major, 2 points).

## Module claim

The administrator dashboard at `/admin/analytics` aggregates real PostgreSQL product data and provides interactive line, bar and pie visualizations, customizable date/category/status filters, realtime updates, and CSV/PDF export of the exact selected slice.

## Access control

Analytics is intentionally an administrator capability.

- frontend route lives under `/admin/*`, so the existing UI RBAC rejects students/instructors;
- all REST endpoints use `allowed_roles("admin")`;
- `/api/ws/analytics` authenticates the JWT and independently requires the current database role to be `admin`;
- a valid non-admin JWT is closed with WebSocket policy code `1008`.

## Real aggregates

`backend/backend/app/services/analytics_service.py` computes the dashboard from the normal domain tables rather than hard-coded chart values:

- `usuarios` → new user registrations;
- `cursos` → courses created;
- `matriculas` → enrollment count, completion rate, daily activity, course ranking and status distribution;
- `avaliacao_curso` → average rating;
- `chat_messages` → social engagement volume.

The service returns one snapshot contract shared by REST, realtime and exports. This prevents the PDF/CSV representation from silently using a different filter or formula than the screen.

## Filters and date ranges

The selected slice includes:

- `start_date`;
- `end_date`;
- optional `category_id`;
- optional `enrollment_status` (`ativa`, `concluida`, `cancelada`).

The default is the most recent 30 days. The date interval can be customized up to 367 days. Invalid inverted ranges/categories/status values return validation errors instead of silently falling back.

Changing filters rebuilds KPIs and all relevant charts. The same parameters are sent to exports and to the realtime subscription.

## Interactive charts

The dashboard implements three owned chart views without importing a chart component library:

1. **Line chart** — daily registrations and enrollments. Data points are mouse/focus inspectable.
2. **Bar chart** — top courses by filtered enrollment count. Bars are keyboard focusable and expose exact values.
3. **Pie chart** — filtered enrollment status distribution with interactive legend/percentage inspection.

The filter controls themselves also provide whole-dashboard interaction, since each selected slice changes both KPIs and visual series.

## Realtime

The browser opens `wss://<host>/api/ws/analytics`, authenticates after connection, then sends:

```json
{
  "type": "analytics.subscribe",
  "filters": {
    "start_date": "2026-08-01",
    "end_date": "2026-08-24",
    "category_id": null,
    "enrollment_status": null
  }
}
```

The server sends an initial `analytics.snapshot` and then recomputes the selected aggregate on a short interval. A stable fingerprint excludes `generated_at`, so the server pushes a new snapshot only when the actual selected data changes. This gives live database-driven updates without browser refresh while avoiding meaningless timestamp-only traffic.

Changing a filter updates the active subscription immediately. Logout/unmount closes the socket and cancels reconnect timers.

## Exports

### CSV

`GET /api/analytics/export.csv` returns UTF-8 CSV containing:

- the selected filter metadata;
- current KPI values;
- daily activity series;
- top-course ranking;
- status distribution.

### PDF

`GET /api/analytics/export.pdf` returns a real `%PDF-1.4` document containing the selected period/filter metadata, KPIs and top-course summary. The implementation is server-side and dependency-free, so the authenticated browser downloads exactly the same aggregate snapshot used by the dashboard.

Both exports require the admin role and receive exactly the filter query currently selected in the UI.

## Evaluation data / reproducibility

`scripts.seed_analytics` extends the existing deterministic Advanced Search/RBAC seeds with idempotent enrollment and recent chat activity rows. It is evaluation/test data stored in the real database schema; the dashboard logic itself has no dependency on seed constants and works against normal application data.

## Automated evidence

`backend/backend/tests/test_analytics.py` covers:

- admin-only dashboard REST access;
- real aggregate presence;
- enrollment-status and category filtering;
- custom date-range validation;
- CSV selected-slice content;
- valid PDF output;
- admin-only WebSocket access;
- a live DB enrollment insertion causing a new realtime snapshot without reload.

`scripts/analytics-check.sh` validates the structural/security contract.

`scripts/analytics-smoke.sh` runs against the Compose PostgreSQL/HTTPS deployment and validates dashboard data, a filtered completion slice, CSV/PDF downloads and a real WSS subscription that updates after a PostgreSQL change.

## Evaluation walkthrough

1. Login with the seeded/evaluation admin account and open `/admin/analytics`.
2. Show the six KPIs and explain their source tables.
3. Inspect line-chart points, bar values and pie legend using mouse and keyboard focus.
4. Change the date range and show KPIs/charts recomputing.
5. Select one category and one enrollment status; show the selected slice changing.
6. Export CSV and verify the selected dates/status appear in the file.
7. Export PDF and verify the same selected period/KPI summary.
8. Keep the dashboard open and create/change data in another client; show the realtime snapshot updating without refresh.
9. Attempt the REST/WebSocket capability as a non-admin to demonstrate RBAC.
10. Show `analytics_service.py`, `test_analytics.py` and the Analytics Gate if the evaluator asks for implementation evidence.
