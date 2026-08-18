# Mandatory evaluation checklist

This checklist is the final gate for the Mandatory Compliance Epic. A box is checked only after the corresponding validation has actually been performed against the delivery candidate.

## Automated gate

From a clean clone configured with a non-example `.env`:

```bash
sh scripts/mandatory-gate.sh
```

Record:

- Date:
- Operating system:
- Docker version:
- Docker Compose version:
- Commit SHA tested:
- Result: PASS / FAIL

The script checks tracked secrets, builds/starts the stack, verifies HTTPS/API/Alembic, runs backend `pytest`, runs frontend lint/build and prints the Git author summary.

## Architecture and deployment

- [ ] repository contains frontend, backend and database components;
- [ ] `docker compose up --build` starts the complete required stack;
- [ ] PostgreSQL starts healthy from an empty volume;
- [ ] Alembic upgrades the empty database to exactly one head;
- [ ] FastAPI starts only after migrations succeed;
- [ ] frontend production image is served without Vite development server;
- [ ] Nginx reverse proxy is the public entrypoint;
- [ ] HTTP redirects to HTTPS;
- [ ] browser-to-backend traffic uses HTTPS through `/api/`;
- [ ] backend port 8000 is not the normal public entrypoint;
- [ ] frontend internal port is not the normal public entrypoint;
- [ ] expected data persists after `docker compose down` and subsequent startup;
- [ ] deployment works from a clean clone without a personal Supabase/database account.

Evidence / notes:

```text
<fill during evaluation rehearsal>
```

## Environment and secrets

- [ ] root `.env.example` documents required variables;
- [ ] real `.env` is ignored by Git;
- [ ] no real private key is committed;
- [ ] no production/database/JWT secret is embedded in frontend bundle configuration;
- [ ] backend fails clearly when required environment variables are absent;
- [ ] `/env` and old diagnostic endpoints do not expose `DATABASE_URL`;
- [ ] client-facing errors do not return raw internal exception details;
- [ ] logs inspected during normal/error flows do not expose passwords, hashes, JWTs or connection strings.

## Authentication and password security

- [ ] valid signup works with email/password;
- [ ] duplicate email is rejected;
- [ ] public signup cannot select `admin`/`instrutor` role;
- [ ] password is never returned in signup response;
- [ ] password is stored only as a salted PBKDF2 hash;
- [ ] two equal passwords produce independently salted hashes;
- [ ] valid login works;
- [ ] wrong password and unknown email return generic invalid-credentials behavior;
- [ ] access token contains expiration and is signed by configured JWT secret;
- [ ] expired token is rejected with 401;
- [ ] forged/invalid token is rejected with 401;
- [ ] missing token is rejected on protected endpoints;
- [ ] role denial returns 403;
- [ ] authorization uses the user's current database role rather than trusting stale role data in a token;
- [ ] logout clears client authentication state as implemented;
- [ ] two simultaneous authenticated sessions remain isolated.

## Frontend validation

Validate at least login, register and search:

- [ ] required fields are enforced;
- [ ] invalid email is rejected;
- [ ] password rules are shown/enforced;
- [ ] password confirmation must match;
- [ ] Terms/Privacy acceptance is required during registration;
- [ ] future/invalid birth date is rejected;
- [ ] search input is normalized/encoded safely;
- [ ] invalid forms do not send requests;
- [ ] registration prevents accidental repeated submit while pending;
- [ ] validation messages are understandable and associated with the relevant input.

## Backend validation

- [ ] request bodies reject unknown fields when strict schemas apply;
- [ ] backend independently rejects weak password and invalid birth date;
- [ ] IDs/path/query values enforce positive/allowed ranges where applicable;
- [ ] review user identity is derived from authentication rather than client-supplied `usuario_id`;
- [ ] role/ownership fields cannot be mass-assigned by normal public payloads;
- [ ] invalid input returns coherent 4xx responses rather than server crashes;
- [ ] OpenAPI reflects the final request contracts.

## Multi-user and concurrency

Use at least two independent users/browser sessions:

- [ ] both users can stay logged in simultaneously;
- [ ] user A never sees user B's authenticated state accidentally;
- [ ] enrollment ownership is enforced;
- [ ] instructor ownership is enforced for enrollment actions;
- [ ] duplicate enrollment attempts cannot create duplicate student/course rows;
- [ ] `scripts/concurrency_smoke.py` produces one success and one conflict for simultaneous duplicate enrollment;
- [ ] progress rows remain unique per enrollment/lesson;
- [ ] lesson progress cannot be changed for a lesson outside the enrolled course;
- [ ] relevant conflicts return predictable 409/403 responses instead of corrupting data.

## Privacy Policy

Test authenticated and unauthenticated:

- [ ] `/privacidade` renders real content, not `PaginaEmConstrucao`;
- [ ] page is reachable directly without login;
- [ ] page is reachable from Footer;
- [ ] authenticated users can also open the public legal route;
- [ ] registration flow no longer displays placeholder Privacy text;
- [ ] policy content matches the final application's actual data behavior;
- [ ] no fictitious integration/data-processing claim remains after optional modules are finalized;
- [ ] page is readable and navigable on mobile/tablet/desktop.

## Terms of Service

- [ ] `/termos` renders real content, not `PaginaEmConstrucao`;
- [ ] page is reachable directly without login;
- [ ] page is reachable from Footer;
- [ ] registration flow no longer displays Lorem Ipsum Terms;
- [ ] Terms and Privacy Policy link to each other consistently;
- [ ] text reflects the final application's actual service/features;
- [ ] page is readable and navigable on mobile/tablet/desktop.

## Responsive and accessible frontend

Check at minimum 320px, 375px, 768px, 1024px and 1440px+ widths:

- [ ] no unexpected horizontal page overflow;
- [ ] Navbar remains usable;
- [ ] Footer remains readable;
- [ ] login/register forms remain usable on short/mobile screens;
- [ ] legal modal remains usable and scrollable when viewport height is constrained;
- [ ] Dashboard cards do not force minimum-width overflow;
- [ ] primary controls have visible focus and are usable by keyboard where applicable;
- [ ] long/error content does not make essential actions unreachable;
- [ ] pages remain usable after resize/orientation changes.

## Stable Chrome browser audit

Record Chrome version:

```text
<version>
```

With DevTools open:

- [ ] Home loads without relevant React/JavaScript warnings/errors;
- [ ] Login valid/invalid flows do not create unhandled exceptions;
- [ ] Register valid/invalid flows do not create unhandled exceptions;
- [ ] Explore/search works without console errors;
- [ ] authenticated navigation works without console errors;
- [ ] direct refresh on SPA routes works;
- [ ] back/forward navigation works;
- [ ] no mixed-content request is present;
- [ ] no normal API request goes directly to `http://localhost:8000`;
- [ ] no unexpected asset 404 is present;
- [ ] no temporary sensitive/debug log remains in the browser console.

## Database schema and ORM

- [ ] SQLAlchemy is used for application persistence;
- [ ] active models match the product schema;
- [ ] experimental `teste_migration` is not part of the active delivery metadata;
- [ ] PK/FK/unique constraints required by current domain rules are present;
- [ ] old experimental Alembic graph is not executed by the clean deployment;
- [ ] `alembic current` is at head;
- [ ] `alembic heads` reports one active head;
- [ ] schema can be reproduced without `Base.metadata.create_all()`.

## README and documentation

- [ ] root `README.md` exists and is in English;
- [ ] required first italicized 42-curriculum sentence is correct for the actual team logins;
- [ ] Description is accurate;
- [ ] Instructions work from a clean clone;
- [ ] Resources list reflects references actually used;
- [ ] AI usage is described honestly;
- [ ] Team Information lists every real member and responsibilities;
- [ ] Project Management matches actual team workflow;
- [ ] Technical Stack and reasons match final implementation;
- [ ] Database Schema matches migrations/models;
- [ ] Features List contains only features actually delivered;
- [ ] contributors per feature are factual;
- [ ] Modules section contains only modules truly completed and totals the intended score;
- [ ] Individual Contributions match real Git/PR evidence;
- [ ] challenges/solutions are specific enough for members to explain.

## Git history and team participation

Run/review:

```bash
git shortlog -sne --all
git log --format='%h %ad %an <%ae> %s' --date=short --all
```

- [ ] every actual team member has real identifiable contribution;
- [ ] author identities are correctly configured;
- [ ] meaningful work is not hidden behind only generic giant commits;
- [ ] current feature/module work can be related to commits/PRs;
- [ ] README ownership agrees with history;
- [ ] no fake/synthetic participation was created for evaluation.

## Automated commands

Record results:

```text
sh scripts/mandatory-gate.sh               PASS / FAIL
cd backend/backend && pytest                PASS / FAIL
cd frontend && npm run lint                 PASS / FAIL
cd frontend && npm run build                PASS / FAIL
sh scripts/clean-install-smoke.sh           PASS / FAIL
python scripts/concurrency_smoke.py ...     PASS / FAIL
```

## Final sign-off

The Mandatory Compliance Epic is ready to close only when:

- [ ] every applicable checkbox above is green;
- [ ] Issues/PRs for mandatory blockers are merged or otherwise resolved;
- [ ] clean-clone validation was performed against the actual delivery commit;
- [ ] stable Chrome audit was performed against the actual delivery commit;
- [ ] team identity/contribution sections are final and evidence-based;
- [ ] no known mandatory blocking defect remains.

Validation commit SHA:

```text
<sha>
```

Validated by:

```text
<team members>
```
