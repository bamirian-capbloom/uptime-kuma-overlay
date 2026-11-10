# monitor-dependencies

Configures one dependency per monitor, gates status notifications, displays confirmed suppression and suppresses dependent browser DOWN toasts. Heartbeat truth and public status remain intact. Seven ordered logical units (including one documented clone-payload correction) preserve the reviewed changes of PRs #1–#6, including regression tests and responsive fixes.

Known semantics: shared authenticated access, process-local coordination, observed check ordering, unknown ancestors can defer indefinitely, provider attempts rather than guaranteed receipt.

## Units and documentation

- [0001-configuration](docs/0001-configuration.md)
- [0002-notification-gate](docs/0002-notification-gate.md)
- [0003-dashboard-ui](docs/0003-dashboard-ui.md)
- [0004-integration-responsive](docs/0004-integration-responsive.md)
- [0005-observation-reconciliation](docs/0005-observation-reconciliation.md)
- [0006-browser-toast-suppression](docs/0006-browser-toast-suppression.md)

- [0006a-clone-payload-safety](docs/0006a-clone-payload-safety.md)

## Tests

Regression tests are embedded in their patches at upstream test paths; the manifest lists each file. This keeps tests versioned with the code under test and runnable by upstream tooling. See the top-level validation and upgrade guides. No separate copied test suite can drift from the replayed tree.
