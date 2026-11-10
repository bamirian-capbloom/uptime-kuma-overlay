# Upgrade, rollback and retirement

## Before applying

1. Read validation.md and confirm the exact supported SHA. This baseline is a v3 beta snapshot; later upstream fixes are excluded deliberately.
2. Back up the live database and configuration with the application stopped; verify restoration in a disposable environment. Replay into a new source directory, never the running service.
3. Run integrity self-tests, fresh lockfile installation, feature regressions, full backend/container suite, lint, build and browser suite. Exercise parent/child DOWN, unknown/paused ancestors, deferred release, reconnect/history ordering, mobile RTL and recovery toast isolation. Record failures and skips; do not deploy on a partial pass.
4. Review the actual code and database changes manually before switching application artifacts. This tooling does not deploy, publish or perform database migrations against an installation.

## Upgrade the upstream pin

Fetch official upstream and the fork; record full SHAs and merge base. Audit both ranges for unrelated changes. Reconstruct a fresh target from the new official SHA and only intended features; inspect auth, Knex migrations, Monitor.beat/sendNotification, push handler, compact/full payloads, socket batching and Vue tooltip/toast contracts. New official fixes may supersede custom hunks. Keep a written inclusion/exclusion ledger.

Regenerate each logical unit and documentation against its new predecessor. Update all source provenance, before/after trees, patch hashes, module hashes and root reference/intended trees. Never keep an old reference-tree claim for a new base. Test all supported module combinations and fresh plus migrated SQLite/MariaDB databases. Compare the entire default target tree to the reviewed intended target. A patch applying cleanly is not sufficient compatibility evidence. Submit changes as a new draft PR, with new validation evidence; merge only after review.

## Rollback

The scripts only create new source directories; delete an unused replay directory to undo local generation. To omit toast recovery, rebuild with `--features monitor-dependencies`; no DB reversal is needed. To remove dependency functionality, stop the service and restore the coordinated pre-overlay code/database backup where possible. If explicitly migrating down, use the matching application migration mechanism to reverse `2026-11-06-0000-dependency-notification-state` before `2026-11-05-0000-add-monitor-dependency`; verify the migration ledger and test on a backup first. Do not blindly call down functions against a live DB. Reversal destroys dependency settings and incident state, affecting future notification/recovery behavior. Merely running bare upstream against a database migrated by this overlay is not a verified rollback.

## Retirement

When upstream implements a feature, compare semantics (including quiet recoveries, deferred alerts and newest-beat toast ordering), not feature names. Replace custom tests only when upstream covers equivalent cases. Plan data migration from custom columns/tables to the native representation; retain an export and backup. Remove dependent units first, regenerate remaining trees/manifests, validate clean replay and run all suites. Preserve provenance and retirement rationale in the PR. No automated reverse-patch or database rollback is provided because it cannot infer production data safety.
