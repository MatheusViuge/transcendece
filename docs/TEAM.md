# Team responsibilities

This document is intentionally evidence-based. A name, role or responsibility is only recorded when it can be reconciled with the final Git/PR history.

## Verified repository identity

| 42/login identity | GitHub identity | Verified repository evidence | Current documented responsibility |
| --- | --- | --- | --- |
| `mviana-v` | `MatheusViuge` | author/maintainer identity associated with the imported baseline and the current repository | repository maintenance, integration review and acceptance of the mandatory-hardening PR stack |

The current `main` history before the mandatory-hardening PR stack contains a single imported baseline commit. It does not provide enough evidence to reconstruct other team members or assign them implementation ownership truthfully.

## Responsibility areas used by the project

The final team table in `README.md` must map real members to the work they actually merge in these areas:

- **Frontend:** React architecture, routes, reusable components, forms, frontend validation, legal pages, responsive behavior and browser-console quality.
- **Backend:** FastAPI architecture, Pydantic contracts, authentication, authorization, SQLAlchemy models, business rules and API tests.
- **Database:** PostgreSQL schema, constraints, transaction/concurrency rules and Alembic migrations.
- **Infrastructure:** Dockerfiles, Docker Compose, reverse proxy, HTTPS, runtime environment and reproducible startup.
- **QA:** automated tests, multi-user scenarios, security regression, clean-clone validation and evaluation rehearsal.
- **Documentation:** README, architecture/schema documentation, module evidence, resources, AI usage and evaluation script.

A member may own more than one area. Planned ownership must not be presented as completed contribution.

## How to update this record

For every real team member, add one row only after there is verifiable work in the repository. Record:

1. the member's actual 42 login;
2. their GitHub identity/commit author identity;
3. primary responsibility areas;
4. concrete features, modules or components they implemented;
5. representative PRs/commits that support the claim;
6. review/integration responsibilities when applicable.

Then mirror the factual summary in the root `README.md` under **Team Information** and **Individual Contributions**.

## Review and integration rules

- GitHub Issues are the source of scope and acceptance criteria.
- Prefer focused branches/PRs tied to an issue.
- PR descriptions must explain validation steps.
- The person merging a PR must understand the change and confirm its tests/acceptance criteria.
- Cross-cutting changes must identify frontend/backend/infra dependencies rather than silently changing another owner's contract.
- AI-assisted changes are still owned by the human team after review; AI assistance is documented separately and never used to fabricate contributor history.

## Final evaluation gate

This file and the README are not considered complete until:

- every actual team member is listed;
- each responsibility maps to real merged work;
- contributor claims match Git commit/PR history;
- the team agrees the descriptions are accurate;
- no placeholder, invented identity or artificial commit is used to satisfy the subject.
