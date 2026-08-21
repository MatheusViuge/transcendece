# Git participation audit

This checklist is used before the final 42 evaluation to verify that repository history reflects real team participation.

## Current baseline observation

Before the mandatory-hardening PR stack, the repository `main` history exposed one imported baseline commit authored as `mviana-v` and associated with the GitHub account `MatheusViuge`.

This is not enough evidence to claim participation by additional team members. Future work must create that evidence through real development, not manufactured commits.

## Per-member audit

For every actual project member, verify:

- [ ] correct 42 login is known;
- [ ] GitHub/commit identity is known;
- [ ] at least one meaningful implementation/documentation/test contribution exists;
- [ ] commits are authored by the person who performed/accepted the work;
- [ ] PRs/issues show the areas in which the member participated;
- [ ] README responsibility/contribution text agrees with the history;
- [ ] the member can explain their attributed code during evaluation.

## Repository-wide audit

- [ ] commit messages are meaningful enough to understand project evolution;
- [ ] unrelated changes are not repeatedly bundled into opaque commits;
- [ ] feature/module PRs reference Issues where practical;
- [ ] no fake authorship or synthetic participation was added;
- [ ] no secrets are present in commits intended for delivery;
- [ ] final README contributors match merged history;
- [ ] all members have real, identifiable participation.

## Useful commands

```bash
git shortlog -sne --all
git log --format='%h %ad %an <%ae> %s' --date=short --all
git log --author='<member>' --oneline --all
```

Use GitHub PR/Issue history together with these commands; commit counts alone do not measure contribution quality.

## Blocking condition

Issue #19 must remain open when any actual team member has no real identifiable contribution in the final repository. Documentation cannot substitute for missing participation, and history must not be fabricated to make the checklist pass.
