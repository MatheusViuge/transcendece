# File Upload Reviewer Checklist

## Automated gate

- [ ] Mandatory Gate is green on the PR head
- [ ] Backend `pytest` includes `test_file_upload.py`
- [ ] `file-upload-check.sh` passes
- [ ] `file-upload-smoke.sh` passes through HTTPS
- [ ] Alembic has exactly one head and database is at head

## Manual Chrome demo

Seed first if needed:

```bash
docker compose exec backend python -m scripts.seed_rbac
```

All seed accounts use `SearchSeed42!`.

- [ ] Login as a seeded user
- [ ] Open the role-specific `Arquivos` link
- [ ] Select PNG/JPEG/WebP/PDF/TXT and confirm client feedback
- [ ] Preview an image/PDF before uploading
- [ ] Upload a larger valid file and observe the progress percentage/bar changing
- [ ] Preview the stored file after upload
- [ ] Download it
- [ ] Delete it and confirm removal
- [ ] Try HTML/SVG and confirm rejection
- [ ] Try a file with misleading extension/MIME and confirm server-side rejection

## Persistence / ownership

The automated smoke already proves these, but reviewers can reproduce when desired:

- [ ] Upload survives backend restart
- [ ] A different normal user cannot fetch/delete the file
- [ ] Admin override works
- [ ] Internal storage filename/path is not exposed to the client

## Merge decision

- [ ] UI is usable on desktop/mobile
- [ ] Preview/progress are visibly demonstrable
- [ ] No security regression found
- [ ] PR is approved for merge
