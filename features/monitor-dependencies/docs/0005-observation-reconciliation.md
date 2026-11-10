# 0005-observation-reconciliation: Stable observations and suppression labels

## Purpose and behavior

Reconciles badges from accepted newest observations and current configuration instead of trusting stale child metadata. History cannot overwrite a newer live observation; disconnect/offline clears claims. Paused ancestor activity uses its own flag even inside paused groups. Displayed status and suppression consume the same accepted beat.

## Modified files, functions and integration points

Adds dependencyActive to compact/full authenticated configuration; no migration. recordDependencyBeat orders live/history beats; dependencyObservations walks the current graph. Monitor.toJSON, toCompactMonitor and socket updateLastBeat, clearDependencyObservations and reconcileDependencyObservations coordinate the payload and UI.

The exhaustive file inventory for this logical unit is:

- `docs/dependency-ui.md`
- `server/compact-monitor.ts`
- `server/model/monitor.js`
- `src/mixins/socket.js`
- `src/monitor-dependency.ts`
- `test/backend-test/test-compact-monitor.ts`
- `test/backend-test/test-heartbeat-serialization.ts`
- `test/backend-test/test-monitor-dependency-socket.ts`
- `test/backend-test/test-server-config.ts`
- `test/e2e/specs/monitor-dependency.spec.js`
- `test/frontend-test/test-monitor-dependency.ts`

Exact changed function/hunk contexts are in the [patch](../patches/0005-observation-reconciliation.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0004-integration-responsive. Apply through the manifest driver, never by glob order. Source: [fork PR #5](https://github.com/bamirian-capbloom/uptime-kuma/pull/5), net diff `d48bcf972fb3e93388fd089e6ef09872c880708b` → `e52926fb3feb736e678007630c98eb34c12830c3`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

Adds dependencyActive to compact/full authenticated configuration; no migration. recordDependencyBeat orders live/history beats; dependencyObservations walks the current graph. Monitor.toJSON, toCompactMonitor and socket updateLastBeat, clearDependencyObservations and reconcileDependencyObservations coordinate the payload and UI.

## Upgrade risks and conflict hotspots

Hotspots: compact/full monitor contracts, timestamp ordering, batching at login, Vue reactive state and heartbeat serialization. Test fixtures must preserve new fields without exposing private dependencies publicly. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

Frontend ordering/reconnect/config-change cases, compact/full payload tests, heartbeat serialization and extended browser reconciliation regressions. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

No database rollback. Removing this unit while keeping UI can reintroduce stale claims, so retire UI/toasts together or replace it with equivalent upstream observation handling. Do not drop dependencyActive without checking paused group semantics. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
