# 0001-configuration: Configuration, validation and authenticated API

## Purpose and behavior

Adds one optional direct dependency per monitor. Validates positive integer IDs, existence and cycles; serializes saves and deletions within the server process. Missing fields preserve an existing dependency on edit and default to null on creation; explicit null clears it. Raw DB aliases cannot bypass validation.

## Modified files, functions and integration points

Adds nullable indexed monitor.dependency_monitor_id with a self foreign key (ON DELETE SET NULL, ON UPDATE CASCADE). Authenticated monitor JSON and compact lists expose dependencyMonitorId. Socket add/edit and deletion paths use saveMonitorWithDependency, validateMonitorDependency and withMonitorDependencyLock. No public dependency configuration endpoint is introduced.

The exhaustive file inventory for this logical unit is:

- `db/knex_migrations/2026-11-05-0000-add-monitor-dependency.js`
- `server/compact-monitor.ts`
- `server/model/monitor.js`
- `server/monitor-dependency.js`
- `server/server.js`
- `test/backend-test/test-compact-monitor.ts`
- `test/backend-test/test-monitor-dependency-socket.ts`
- `test/backend-test/test-monitor-dependency.ts`
- `test/backend-test/test-monitor.ts`
- `test/backend-test/test-server-config.ts`
- `test/fixtures/monitor-columns.json`

Exact changed function/hunk contexts are in the [patch](../patches/0001-configuration.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires no earlier unit. Apply through the manifest driver, never by glob order. Source: [fork PR #1](https://github.com/bamirian-capbloom/uptime-kuma/pull/1), net diff `f6f6e6da26a29176ae0a2c928f507674eb593f66` → `d3f47d768bb87f67afd211153b13c8e994b06956`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

Adds nullable indexed monitor.dependency_monitor_id with a self foreign key (ON DELETE SET NULL, ON UPDATE CASCADE). Authenticated monitor JSON and compact lists expose dependencyMonitorId. Socket add/edit and deletion paths use saveMonitorWithDependency, validateMonitorDependency and withMonitorDependencyLock. No public dependency configuration endpoint is introduced.

## Upgrade risks and conflict hotspots

The shared authenticated-access model is preserved; this is not tenant isolation. The lock is process-local. Conflicts concentrate in server/server.js add/edit/delete handlers, Monitor serialization and compact payload types. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

Migration up/down, legacy payloads, invalid IDs, cycles including opposing concurrent edits, group/monitor deletion, compact payload and authenticated Socket.IO round trips. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

Removing this unit requires retiring all later units. Stop the application, back up the database, then explicitly reverse the two custom migrations in reverse order using the matching application migration tooling, or restore the pre-overlay database. Dropping this column destroys dependency settings. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
