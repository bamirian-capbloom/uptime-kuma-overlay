# 0007-recovery-cleanup: Dismiss DOWN toasts on accepted recovery

## Purpose and behavior

Extends existing per-monitor DOWN tracking: a newest accepted UP dismisses all outstanding DOWN toast IDs for that monitor. Other monitors remain untouched; pending/maintenance and stale recovery do not dismiss. A later DOWN can show a new toast. Normal success notifications keep existing behavior.

## Modified files, functions and integration points

No schema/API change. DependencyDownToasts.reconcile accepts the current beats map and checks UP; socket reconcileDependencyObservations passes those beats. Reuses tracking from monitor-dependencies rather than introducing another tracker.

The exhaustive file inventory for this logical unit is:

- `src/dependency-down-toasts.ts`
- `src/mixins/socket.js`
- `test/frontend-test/test-dependency-down-toasts.ts`

Exact changed function/hunk contexts are in the [patch](../patches/0007-recovery-cleanup.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0006-browser-toast-suppression. Apply through the manifest driver, never by glob order. Source: [fork PR #7](https://github.com/bamirian-capbloom/uptime-kuma/pull/7), net diff `6422ad9ce8e91bb023e991b002614bbb7f5e4cc6` → `7162f0d0fac3bf51b31fdfcab4bc3f2f285958c6`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

No schema/API change. DependencyDownToasts.reconcile accepts the current beats map and checks UP; socket reconcileDependencyObservations passes those beats. Reuses tracking from monitor-dependencies rather than introducing another tracker.

## Upgrade risks and conflict hotspots

Depends on the entire monitor-dependencies module as packaged, especially browser-toast-suppression and accepted-beat ordering. This release cannot apply recovery independently to bare upstream. Future extraction of a neutral toast tracker is possible but requires new patch/tree/test evidence. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

Recovery tests in test-dependency-down-toasts.ts cover accepted UP, another monitor remaining DOWN, later DOWN, stale UP, repeated reconciliation and pending/maintenance. Run the complete frontend test file with and without this module. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

Remove this module by rebuilding from the pinned base with only monitor-dependencies; no DB rollback. Existing browser toasts vanish on page reload. Upstream retirement requires equivalent accepted-observation semantics and per-monitor isolation. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
