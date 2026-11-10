# 0002-notification-gate: Durable notification suppression

## Purpose and behavior

Gates scheduled and push DOWN transitions/repeats across the complete ancestor chain. Active DOWN ancestors suppress; unknown/PENDING ancestors defer. Paused and maintenance ancestors do not block by themselves, but traversal continues. Silent incidents recover silently; previously announced incidents retain recovery. Deferred DOWN sends on the next child check after release. Certificate/domain alerts and real heartbeat statuses remain unchanged.

## Modified files, functions and integration points

Creates monitor_notification_state keyed by monitor_id (cascade delete), status, incident_open and deferred. processDependencyNotification serializes decisions per monitor and persists observations before sending; dependencyMetadata resolves ancestors. Monitor.beat and push /api/push/:pushToken use the gate; live private heartbeat payloads add dependencyNotification metadata. History schema is unchanged.

The exhaustive file inventory for this logical unit is:

- `db/knex_migrations/2026-11-06-0000-dependency-notification-state.js`
- `docs/dependency-notifications.md`
- `server/dependency-notification.js`
- `server/model/monitor.js`
- `server/routers/api-router.js`
- `test/backend-test/test-api.ts`
- `test/backend-test/test-dependency-notification.ts`
- `test/backend-test/test-monitor-beat.ts`

Exact changed function/hunk contexts are in the [patch](../patches/0002-notification-gate.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0001-configuration. Apply through the manifest driver, never by glob order. Source: [fork PR #2](https://github.com/bamirian-capbloom/uptime-kuma/pull/2), net diff `d3f47d768bb87f67afd211153b13c8e994b06956` → `160ab3af8b29089ae3b897372f3c9e76cd2c38df`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

Creates monitor_notification_state keyed by monitor_id (cascade delete), status, incident_open and deferred. processDependencyNotification serializes decisions per monitor and persists observations before sending; dependencyMetadata resolves ancestors. Monitor.beat and push /api/push/:pushToken use the gate; live private heartbeat payloads add dependencyNotification metadata. History schema is unchanged.

## Upgrade risks and conflict hotspots

This is single-process coordination and tracks provider attempts, not receipt. A crash around external delivery can duplicate a notification; unknown ancestors may defer forever. Hotspots: Monitor.beat/sendNotification, push handler, migrations, heartbeat serialization. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

State-machine unit tests, push API transitions and overlapping pushes, retry/repeat semantics, slow notification/delete races. Later integration tests exercise real webhooks, restart durability and privacy. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

Back up first and stop the server. Retiring this unit also retires downstream UI/toast units. Reverse notification-state migration before dependency-column migration only when removing configuration too. Losing incident state can cause duplicate DOWN or orphan recovery on restart; prefer restoring a coordinated code/database snapshot. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
