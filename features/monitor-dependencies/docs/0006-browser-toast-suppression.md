# 0006-browser-toast-suppression: Suppress and track dependency DOWN toasts

## Purpose and behavior

Tracks monitor DOWN toast IDs through DependencyDownToasts.show/reconcile. Suppressed or stale DOWN events do not create toasts; newly suppressed monitors have their existing DOWN toasts dismissed. Manual close removes IDs. Unrelated errors/success toasts retain their existing lifecycle and configured timeout.

## Modified files, functions and integration points

No schema or wire change. Adds src/dependency-down-toasts.ts and integrates a markRaw instance into socket data and heartbeat handling. Uses current dependency observations and toRaw identity to reject stale beats.

The exhaustive file inventory for this logical unit is:

- `src/dependency-down-toasts.ts`
- `src/mixins/socket.js`
- `test/frontend-test/test-dependency-down-toasts.ts`

Exact changed function/hunk contexts are in the [patch](../patches/0006-browser-toast-suppression.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0005-observation-reconciliation. Apply through the manifest driver, never by glob order. Source: [fork PR #6](https://github.com/bamirian-capbloom/uptime-kuma/pull/6), net diff `e52926fb3feb736e678007630c98eb34c12830c3` → `6422ad9ce8e91bb023e991b002614bbb7f5e4cc6`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

No schema or wire change. Adds src/dependency-down-toasts.ts and integrates a markRaw instance into socket data and heartbeat handling. Uses current dependency observations and toRaw identity to reject stale beats.

## Upgrade risks and conflict hotspots

Hotspots: vue-toastification ID/onClose contract, Vue proxy identity, socket heartbeat order and reconciliation. Recovery cleanup is a separate dependent module; suppression alone does not implement UP dismissal. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

test-dependency-down-toasts.ts covers suppressed arrivals, later ancestor failure, per-monitor isolation, multiple toast IDs, manual close, unchanged timeout and stale events. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

No data migration. Removing toast-lifecycle first allows removal of this tracking unit; restoring original socket toast.error restores baseline behavior. Retire against upstream only after confirming per-monitor suppression and stale-event handling are equivalent. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
