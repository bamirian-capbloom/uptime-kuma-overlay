# 0006b-dashboard-suppression-causes: explain dashboard suppression

## Purpose and behavior

Implements [issue #2](https://github.com/bamirian-capbloom/uptime-kuma-overlay/issues/2). The old Quick Stats card repeated suppressed monitor links and badges without visibly naming the blocker. The new **Suppressed failure alerts (count)** summary lists the affected monitor, its actual DOWN state, and the current blocking dependency with a DOWN badge. Both monitor names link to their details. A native keyboard-accessible disclosure shows the complete ordered dependency path without entering configuration.

The configured direct dependency is not substituted for the current blocker. For Website → Gateway → Router, Website can be DOWN while Gateway is UP and an active DOWN Router blocks Website's failure alerts. The UI names Router in that case. Multiple DOWN ancestors use the same closest-active-DOWN selection as the existing resolver. This explains notification policy, not proven physical causation. See [Understanding notification dependencies](understanding-dependencies.md).

Rows come from the existing authenticated dependencyObservations store and configuration. Recovery, edits, pause, deletion and reconnect/history updates therefore follow the existing accepted-observation logic. The summary disappears when no confirmed suppression is available, including disconnect. Actual health/counts are preserved. Monitor-details changes from issue #3 are outside this unit.

## Upstream files and functions modified

- `src/components/DependencySuppressionSummary.vue` (new): `rows` joins existing monitor/blocker/ancestor observations into the private summary; native details/summary links expose paths. The component does not calculate a new suppression policy. Path DOM is rendered when its disclosure is expanded. Scoped styles provide wrapping desktop columns and mobile cards, logical spacing, escaped/bidi-isolated names, and inherited dark-mode colors.
- `src/pages/DashboardHome.vue`: replaces the old repeated badge list and removes its redundant suppressedMonitors computed property; mounts the new summary.
- `src/lang/en.json`: adds count, column, disclosure and accessible table-description strings. Other locales use the existing English fallback.
- `test/e2e/specs/dependency-suppression-summary.spec.js` (new): real authenticated push/form scenarios cover closest/indirect blockers, links/paths, health counts, recovery, edits, pause/deletion, offline/reconnect, stale history and escaped long names on narrow dark RTL screens.
- `test/e2e/specs/monitor-dependency.spec.js`: updates the former duplicate-badge assertions to require the single sidebar badge plus the explanatory summary and correct blocker. Existing behavior coverage is retained.

## Dependencies and baseline

Official upstream `f6f6e6da26a29176ae0a2c928f507674eb593f66`, after monitor-dependencies units 0001–0006a. The unit precedes optional toast-lifecycle 0007. Both supported selections include this dashboard enhancement; it is part of monitor-dependencies, not an independently selectable feature. The feature manifest pins patch SHA-256 and exact before/after trees. All original PR patch bytes remain unchanged; the optional toast unit's tree checkpoints are regenerated for its new predecessor.

Root intended.correction_units now also declares 0006b as an additional intended delta from the original fork reference. Default replay reverses the declared additions in an alternate index and must reconstruct the exact original fork tree and changed-file allowlist. This records the new feature honestly rather than pretending the customized output still equals the old fork alone.

## API and schema effects

None. No database migration, persisted setting, notification state or public/private API payload is added. Existing dependency configuration, accepted observations and ancestor IDs are sufficient. The component is mounted only in the authenticated dashboard. Notification delivery, deferred incidents, repeats, status calculations and browser toast lifecycle are unchanged.

## Upgrade risks and conflict hotspots

DashboardHome's card structure, authenticated root-store contracts, DependencyMonitor/SuppressionObservation fields, Status styling, translation fallback and Bootstrap/table/responsive styles are the main hotspots. Future changes to blocker selection or observation freshness must continue to be owned by the existing resolver, not duplicated in this presentation. Review mobile wrapping and keyboard disclosure behavior after Vue/Bootstrap/RTL tooling upgrades. English fallback is provided; native translations remain future work. The path is a configured chain, not a root-cause claim.

## Tests and verification

Run `npm run test-e2e -- dependency-suppression-summary --max-failures=0` with the pinned application's normal browser prerequisites. The three new scenarios plus six setup checks passed locally. Existing dependency browser tests are updated alongside the component. Run the full browser suite, lint, production build and existing feature regressions; validate fresh replay for monitor-dependencies alone and with toast-lifecycle. The repository CI performs both complete variants. See docs/issue-2-validation.md for current evidence, transient harness corrections and test-image provenance.

## Rollback and retirement

No database rollback is needed. Rebuild the previously validated overlay revision to restore the old dashboard presentation while retaining the same data. Do not reverse-patch a running or dirty checkout. If retiring only this unit, remove it from the module, regenerate the toast predecessor/output checkpoints, intended tree, root delta ledger/allowlist and affected checksums, then verify clean replay and browser coverage. An upstream replacement must retain correct indirect blockers, independently observed health, private-only data and accessible links/path inspection. Test-container updates must use a separate consistent copy of existing data; do not discard the user's configured volume.
