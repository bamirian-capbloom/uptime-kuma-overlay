# 0006a-clone-payload-safety: derived activity is not configuration

## Purpose and behavior

Full browser validation of the exact merged fork found that cloning an HTTP monitor failed to save. PR #5 adds `dependencyActive` to full monitor JSON for accurate paused-ancestor display. The clone form forwards that derived field to Socket.IO `add`; the generic bean import then tries to persist a nonexistent `dependency_active` database column. Ordinary new monitors omit the field, explaining why configuration regression tests did not detect this.

This corrective unit strips both camelCase and raw snake_case derived activity aliases from add/import payloads. It preserves the separately validated dependencyMonitorId and does not trust client activity metadata. The clone flow can create a monitor normally. This is a deliberate, narrow correction beyond merged fork PRs #1–#7, not unrelated fork divergence.

## Modified files and functions

- `server/server.js`: Socket.IO `add` handler, `frontendOnlyProperties` sanitization immediately before `bean.import(monitor)`. Two entries are added; existing validated configuration handling is unchanged.
- `test/backend-test/test-monitor-dependency-socket.ts`: authenticated lifecycle integration test now creates a monitor with both derived activity aliases and a valid dependency, then asserts the dependency persists. The existing browser `monitor-list-actions.spec.js` clone scenario independently exercises the actual UI path without changing that test to hide the failure.

## Dependencies and baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66`, after units 0001–0006. Ordered before toast-lifecycle 0007. The module manifest records exact patch SHA-256 and before/after trees. The root manifest retains the original merged fork tree in `reference.tree` and records the corrected customized tree separately in `intended.tree`. Default replay automatically reverses this declared corrective unit in an alternate index and requires exact reconstruction of the reference tree plus an exact two-file divergence allowlist. `intended.difference_from_reference` explicitly lists the two changed files and rationale.

## API and schema effects

No new columns, tables or API response fields. Incoming derived `dependencyActive` and `dependency_active` values are ignored for monitor creation; they cannot create DB columns or override server-derived activity. Persisted dependency configuration still follows the original validation and cycle rules. No migration is needed.

## Upgrade risks and conflict hotspots

The upstream add handler's field sanitation list and generic bean import are the only production hotspot. If upstream replaces generic import with an allowlisted schema, this patch may become unnecessary. Check other read-only fields and clone payload contracts when upgrading. Avoid removing the legitimate `active` configuration field or validated `dependencyMonitorId` when resolving conflicts.

## Tests and verification

The baseline full Chromium run exposed the clone save timeout. Re-run the corrected Socket.IO test, all 59 feature tests, lint/build, and the complete browser suite, including `clones a monitor into the list`. Linux CI exercises both supported feature selections. See docs/validation.md for final results; do not interpret the earlier exact-fork passing feature subset as proof that the clone path worked.

## Rollback and retirement

No DB rollback is required. Removing this unit restores the known clone regression, so keep it while retaining the derived payload field unless upstream implements equivalent filtering. Remove its regression only if upstream covers both aliases and preserves validated dependency settings. Regenerate toast-lifecycle tree checkpoints after retirement. Rebuild from the pin rather than reverse-patching a running checkout.
