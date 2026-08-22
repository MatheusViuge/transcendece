# Advanced Search review checklist

Parent Epic: #25

## Automated

- [ ] `npm run lint` passes
- [ ] `npm run build` passes
- [ ] `sh scripts/search-check.sh` passes
- [ ] backend regression passes, including `tests/test_advanced_search.py`
- [ ] combined filters + sorting + pagination test passes
- [ ] invalid search parameters return 422
- [ ] HTTPS deployment serves `/api/search/courses`
- [ ] Framework/ORM, Design System and PWA regressions remain green

## Manual browser review

- [ ] `/explorar` loads persisted results without console errors
- [ ] text search works with normal, accented and special-character input
- [ ] category, level, instructor and price filters can be combined
- [ ] sorting field and direction change result order
- [ ] pagination preserves the active search state
- [ ] empty result state is clear
- [ ] loading/error states are understandable
- [ ] copied URL reproduces the same search state in another tab
- [ ] refresh preserves the same state
- [ ] Back/Forward restores previous search states
- [ ] mobile and keyboard navigation remain usable

## Module gate

- [ ] #46 validated
- [ ] #47 validated
- [ ] #48 validated
- [ ] #49 evidence recorded
- [ ] Epic #25 ready to merge/close
