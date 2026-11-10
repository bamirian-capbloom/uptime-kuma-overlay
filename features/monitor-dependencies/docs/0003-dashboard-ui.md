# 0003-dashboard-ui: Dependency selection and suppression indicators

## Purpose and behavior

Adds the dependency selector with client cycle filtering and an accessible suppression badge on authenticated list, details and dashboard views. Labels describe suppressed failure alerts alongside the real DOWN state. Tooltip names remain escaped text. English feature strings provide fallback for other locales.

## Modified files, functions and integration points

No new migration. Uses dependencyMonitorId from configuration and private live metadata; dependencyChain and initial dependencyObservations helpers feed DependencySuppression.blocker/explanation/showTooltip. socket updateLastBeat/reconciliation and EditMonitor save/form initialization integrate the feature. Public status pages remain outside this UI.

The exhaustive file inventory for this logical unit is:

- `docs/dependency-ui.md`
- `src/components/DependencySuppression.vue`
- `src/components/MonitorListItem.vue`
- `src/lang/en.json`
- `src/mixins/socket.js`
- `src/monitor-dependency.ts`
- `src/pages/DashboardHome.vue`
- `src/pages/Details.vue`
- `src/pages/EditMonitor.vue`
- `test/e2e/specs/monitor-dependency.spec.js`
- `test/e2e/specs/monitor-list-actions.spec.js`
- `test/frontend-test/test-monitor-dependency.ts`

Exact changed function/hunk contexts are in the [patch](../patches/0003-dashboard-ui.patch); new files include their complete implementation. Tests and historical operator docs are part of the unit, not installed separately.

## Dependencies and applicable baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Requires 0002-notification-gate. Apply through the manifest driver, never by glob order. Source: [fork PR #3](https://github.com/bamirian-capbloom/uptime-kuma/pull/3), net diff `160ab3af8b29089ae3b897372f3c9e76cd2c38df` → `82a3d2108c2de6142f974af799df430176c787bc`. The manifest pins both input/output Git tree objects and the patch SHA-256. This is a complete logical PR unit including reviewed fixes, not each transient commit.

## API and schema effects

No new migration. Uses dependencyMonitorId from configuration and private live metadata; dependencyChain and initial dependencyObservations helpers feed DependencySuppression.blocker/explanation/showTooltip. socket updateLastBeat/reconciliation and EditMonitor save/form initialization integrate the feature. Public status pages remain outside this UI.

## Upgrade risks and conflict hotspots

Hotspots: socket heartbeat/history handlers, EditMonitor fields, DashboardHome rows, Details and MonitorListItem markup, locale keys and shared Tooltip positioning. This historical unit is completed by observation-reconciliation before release; do not ship intermediate units. Only complete feature boundaries are supported outputs; intermediate patch trees are integrity checkpoints.

## Tests and verification

Frontend graph/observation tests and Playwright configuration persistence, escaped labels, keyboard focus/Escape, public visibility and dependency badge scenarios. Run `python3 scripts/validate.py SOURCE NEW_DESTINATION` for fresh replay, feature regression tests and production build; add `--full` for the full backend/container and browser suites. CI runs the full path. New unit-specific passing evidence is recorded in `docs/validation.md`; historical reports bundled in patches do not substitute for it. A pass requires zero unexpected failures; inspect skips and runner prerequisites.

## Rollback and retirement

No data rollback is needed when removing UI alone, but server suppression would remain active. Remove dependent observation and toast units at the same time; communicate invisible suppression to operators or retire the complete module. Never reverse patches in a running or dirty application checkout. Generate a fresh selected-feature tree, test it, and switch application artifacts in a maintenance window. Re-test removal against a restored database before production rollback.
