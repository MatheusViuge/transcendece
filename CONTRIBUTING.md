# Contributing

The project uses GitHub Issues and pull requests to keep work traceable for the 42 evaluation.

## Before starting work

1. Choose or create an Issue with clear acceptance criteria.
2. Make sure the task is assigned to the person actually implementing it.
3. Create a focused branch from the correct integration base.

Suggested branch names:

```text
feat/<issue>-short-description
fix/<issue>-short-description
test/<issue>-short-description
docs/<issue>-short-description
infra/<issue>-short-description
```

## Commits

Commits must represent real work performed by their actual author.

Good examples:

```text
feat: add role management endpoint (#57)
fix: prevent duplicate active enrollment (#15)
test: cover revoked api keys (#55)
docs: document analytics module (#90)
```

Avoid:

- `update` / `fix stuff` / `final`;
- one giant commit containing unrelated features;
- commits made only to manufacture activity;
- changing author metadata to make another person appear to have contributed;
- committing generated secrets, `.env` files or private keys.

Each team member must configure their own Git identity before contributing:

```bash
git config user.name "<real-name-or-handle>"
git config user.email "<email-associated-with-github>"
```

## Pull requests

Prefer one focused PR per Issue. A PR should contain:

- the Issue reference;
- what changed;
- why it changed;
- validation/test instructions;
- dependencies on other PRs or modules;
- screenshots only when they materially help UI review;
- no claim that a test passed unless it was actually executed.

PRs should remain draft while acceptance criteria are not demonstrably satisfied.

## Review

Reviewers must verify:

- code matches the Issue scope;
- frontend/backend contracts remain compatible;
- validation and error handling exist;
- security-sensitive paths do not rely only on the UI;
- tests were added or updated when appropriate;
- documentation is updated when behavior or module evidence changed;
- the author can explain the implementation.

## Merge strategy

Merge only after dependencies are available and the PR is reviewable against its intended base. For stacked PRs, merge from the bottom of the stack upward or retarget the next PR after its base is merged.

Do not squash/rewrite history merely to hide who implemented the work. Repository history should remain understandable and attributable.

## AI-assisted work

AI assistance may be used and must be disclosed in the README according to the subject. Human team members remain responsible for:

- reviewing generated suggestions;
- testing changes;
- understanding the code;
- correcting defects;
- intentionally committing/merging accepted work.

AI output must never be used to fabricate a human contributor or a fake commit history.
