# File Upload & Management — Evaluation Evidence

## Module

**Minor — 1 point**

Epic: #28  
Children: #62, #63, #64, #65

When merged, the cumulative roadmap becomes **11/19**.

## Architecture

The module is generic and reusable. It is intentionally not tied to avatars so that later features, especially User Management (#29), can reuse the same storage and ownership layer.

- Metadata: PostgreSQL table `uploaded_files`
- Physical storage: dedicated Docker volume `file_storage`
- Internal names: server-generated UUIDs
- Ownership: `owner_id` bound to the authenticated user
- Authorization: owner or admin for metadata/content/delete
- Public raw paths: never exposed
- Content access: authenticated `/api/files/{id}/content`

## Supported types and limits

| Type | Extensions | Max size |
| --- | --- | ---: |
| PNG | `.png` | 8 MB |
| JPEG | `.jpg`, `.jpeg` | 8 MB |
| WebP | `.webp` | 8 MB |
| PDF | `.pdf` | 12 MB |
| UTF-8 text | `.txt` | 2 MB |

HTML and SVG are deliberately excluded because serving active content would unnecessarily expand the XSS/active-document attack surface.

The reverse proxy accepts up to 13 MB so the largest valid multipart request can reach FastAPI, while the backend enforces the exact per-type policy.

## Server-side validation

The backend validates all of the following independently of the browser:

1. declared MIME type;
2. extension allowlist for that MIME;
3. maximum size while streaming;
4. file signature/magic bytes for PNG/JPEG/WebP/PDF;
5. UTF-8/no-NUL validation for TXT;
6. non-empty content;
7. normalized display filename;
8. server-generated storage filename;
9. cleanup of partial/invalid uploads.

Renaming a file extension does not bypass the signature check.

## Lifecycle

Endpoints:

- `GET /api/files` — list current user's files
- `POST /api/files` — multipart upload
- `GET /api/files/{id}` — metadata
- `GET /api/files/{id}/content` — authenticated inline content
- `GET /api/files/{id}/content?download=true` — authenticated download
- `DELETE /api/files/{id}` — delete metadata + physical object

Administrators may inspect/delete another user's file; normal users cannot.

## Frontend

Authenticated routes:

- `/aluno/arquivos`
- `/instrutor/arquivos`
- `/admin/arquivos`

The page provides:

- client-side type/size validation for fast feedback;
- pre-upload image/PDF preview;
- real Axios `onUploadProgress` progress reporting;
- authenticated post-upload preview using Blob URLs;
- TXT preview;
- authenticated download;
- delete confirmation;
- responsive layout and accessible labels/progress semantics.

Client-side validation is UX only; the backend remains authoritative.

## Persistence

`docker-compose.yml` mounts:

```text
file_storage:/app/storage/uploads
```

The CI smoke uploads a file, restarts the backend container, authenticates again, and verifies that the exact bytes remain downloadable before deletion.

## Automated evidence

- `backend/backend/tests/test_file_upload.py`
- `scripts/file-upload-check.sh`
- `scripts/file-upload-smoke.sh`
- Mandatory Gate integration

Automated coverage includes:

- multiple valid file types;
- oversized files;
- unsupported active content;
- extension/MIME mismatch;
- invalid signature;
- malicious/path-like filename normalization;
- owner isolation;
- admin override;
- physical cleanup;
- persistence across backend restart;
- HTTPS/Nginx integration.

## Manual demo

1. Run the seed already used by the project:
   `docker compose exec backend python -m scripts.seed_rbac`
2. Log in as any seeded user (`SearchSeed42!`).
3. Open that role's `Arquivos` page.
4. Select a valid image/PDF/TXT and observe preview before upload.
5. Upload a sufficiently large valid file and observe progress changing.
6. Preview/download the stored file.
7. Delete it and confirm it disappears.
8. Try an unsupported HTML/SVG or a renamed invalid image and observe rejection.

## README reconciliation

The root README remains intentionally deferred to the final project reconciliation (#16/#18/#33). This file is the module-specific source of evaluation evidence until then.
