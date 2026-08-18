# Clean-install validation

Issue #20 is validated from a fresh clone or a directory that does not contain previous build artifacts, virtual environments, `node_modules` or Docker bind mounts.

## 1. Clone and environment

```bash
git clone <repository-url>
cd transcendece
cp .env.example .env
```

Replace both example secrets in `.env`. Do not reuse personal/production credentials.

## 2. Optional destructive reset

Only when intentionally testing an empty database and disposable local volumes:

```bash
docker compose down -v
```

This command deletes the local PostgreSQL and generated TLS volumes. It is intentionally not run by the smoke script.

## 3. Automated deployment smoke

```bash
sh scripts/clean-install-smoke.sh
```

The script verifies:

- Docker Compose configuration parses;
- the full stack builds and starts;
- `https://localhost/api/status` becomes healthy;
- HTTP redirects to HTTPS;
- frontend routes respond through the HTTPS proxy;
- backend/frontend internal ports are not public on 8000/8080;
- Alembic reports the database at a single active head;
- no container reports an unhealthy status.

The local certificate is self-signed, so the script uses `curl --insecure` only for local TLS verification. This does not disable TLS in the application.

## 4. Manual mandatory smoke

With the stack left running:

- [ ] open `https://localhost` in the current stable Chrome;
- [ ] acknowledge the local self-signed certificate warning if necessary;
- [ ] create a new account;
- [ ] log in;
- [ ] verify `/privacidade` and `/termos` without authentication;
- [ ] navigate public and authenticated routes;
- [ ] inspect Console for relevant errors/warnings;
- [ ] inspect Network for mixed content or direct `http://localhost:8000` requests;
- [ ] execute a normal write flow, then restart the stack;
- [ ] confirm expected data persists after `docker compose down` followed by `docker compose up -d`;
- [ ] execute the multi-user/concurrency scenario documented for Issue #15.

## 5. Evidence to record

Record in the validation PR/checklist:

- operating system / Docker version;
- stable Chrome version;
- date of the clean-clone run;
- result of `sh scripts/clean-install-smoke.sh`;
- result of frontend `npm run lint` and `npm run build`;
- result of backend `pytest`;
- any failure found and the Issue/PR that fixed it.

Issue #20 must not be closed based only on the existence of this script; the clean-clone procedure must actually be executed successfully.
