# 0004-integration-responsive: Integration coverage and mobile RTL fixes

## Purpose and behavior

Adds real webhook, restart, push, retry, public privacy and MariaDB migration integration coverage. Keeps long monitor URLs and dependency explanations inside mobile/RTL viewports. Includes shared Tooltip physical centering fix and Details URL wrapping because the dependency feature exposed those layout defects.

## Modified files, functions and integration points

No schema/API change. Changes Tooltip inline transform and Details URL wrapping; extends dependency browser scenarios. Tests launch disposable servers, SQLite databases, MariaDB containers and webhook listeners. The included historical test report is provenance, not evidence for a new replay.

The exhaustive file inventory for this logical unit is:

- `docs/dependency-integration-testing.md`
- `src/components/Tooltip.vue`
- `src/pages/Details.vue`
- `test/backend-test/test-dependency-delivery.ts`
- `test/backend-test/test-dependency-mariadb.ts`
- `test/e2e/specs/monitor-dependency.spec.js`

Exact changed function/hunk contexts are in the [patch](../patches/0004-integration-responsive.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0003-dashboard-ui. Apply through the manifest driver, never by glob order. Source: [fork PR #4](https://github.com/bamirian-capbloom/uptime-kuma/pull/4), net diff `82a3d2108c2de6142f974af799df430176c787bc` → `d48bcf972fb3e93388fd089e6ef09872c880708b`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

No schema/API change. Changes Tooltip inline transform and Details URL wrapping; extends dependency browser scenarios. Tests launch disposable servers, SQLite databases, MariaDB containers and webhook listeners. The included historical test report is provenance, not evidence for a new replay.

## Upgrade risks and conflict hotspots

Shared Tooltip affects other consumers: inspect RTL and LTR tooltip alignment on upgrades. Container tests require Docker; integration listeners require local networking. Historical docs contain old counts and must not be treated as current CI status. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

test-dependency-delivery.ts, test-dependency-mariadb.ts and monitor-dependency.spec.js cover chain releases, provider ordering, restarts, privacy, paused/unknown ancestors and 390px RTL bounds. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

No persistent production data changes. If upstream fixes the responsive defects, retire only the redundant hunks after re-running browser regressions; retain behavioral coverage. Later units were generated after these layout fixes and need regeneration if this unit is removed. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
