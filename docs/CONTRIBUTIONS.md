# Individual contribution evidence

This document records the method used to build the final **Individual Contributions** section of the root README. It must remain consistent with real repository history.

## Evidence rules

A contribution may be attributed to a member when at least one repository artifact supports it, preferably:

- a merged pull request authored by the member;
- meaningful commits authored by the member;
- issue discussion plus commits/PRs showing implementation;
- review/integration work that is visible in PR history.

Do not use fabricated commits, rewritten authorship or unsupported statements to satisfy the subject.

## Evidence currently available

### `mviana-v` / `MatheusViuge`

Verified repository evidence available before the current mandatory-hardening stack:

- author identity of the imported baseline commit;
- owner/maintainer of `MatheusViuge/transcendece`;
- maintainer account under which the current mandatory-hardening draft PR stack is being prepared for review.

Current mandatory-hardening areas represented by draft PRs include:

- legal pages and public-route behavior;
- frontend form validation and browser-console cleanup;
- responsive hardening;
- frontend production containerization;
- root Docker Compose and HTTPS reverse proxy;
- sensitive endpoint and secret management hardening;
- password hashing and backend validation;
- Alembic clean migration line;
- multi-user/concurrency hardening;
- mandatory documentation.

These draft changes are AI-assisted. They only become accepted project contribution after the human team reviews, understands, tests and intentionally merges them.

## Per-member final entry format

For every actual member, the final README entry should contain:

### `<42-login>`

**Primary responsibilities**

- concrete responsibility area;
- concrete responsibility area.

**Implemented work**

- feature/component/module with representative PR or commit;
- feature/component/module with representative PR or commit.

**Challenges and solutions**

- specific technical challenge;
- decision or implementation used to solve it;
- trade-off or limitation the member can explain during evaluation.

**Module participation**

- selected Major/Minor module(s) in which the member implemented meaningful work;
- evidence used to support that attribution.

## Final reconciliation procedure

Before evaluation:

1. list merged PRs and meaningful commits by author;
2. group them by feature/module;
3. compare those groups with the Team Information and Features List sections;
4. ask each member to review their entry for factual accuracy;
5. remove planned work that was never merged;
6. ensure AI assistance is disclosed without attributing AI output as an independent human contributor;
7. ensure every member can explain the code attributed to them.

## Completion gate

Issue #18 is only truly complete when:

- every actual member has a detailed entry;
- entries contain concrete features/components/modules;
- challenges and solutions are described factually;
- claims can be traced to the final Git/PR history;
- the root README mirrors this information;
- the team reviews the final text.
