# monitor-dependencies

Configures one dependency per monitor, gates status notifications, displays confirmed suppression and suppresses dependent browser DOWN toasts. Heartbeat truth and public status remain intact. Eight ordered logical units preserve the reviewed changes of PRs #1–#6, the documented clone-payload correction, and the issue #2 dashboard suppression explanation, including regression tests and responsive fixes.

Known semantics: shared authenticated access, process-local coordination, observed check ordering, unknown ancestors can defer indefinitely, provider attempts rather than guaranteed receipt.

## Interpreting dependencies

A configured dependency controls failure notifications while each monitor retains its own observed health. An UP child and DOWN ancestor can reflect different check times, check coverage, failover or partial functionality; persistent disagreement in a strict dependency deserves investigation.

Read [Understanding notification dependencies](docs/understanding-dependencies.md) for practical examples, the distinction between a configured dependency and its current blocker, and guidance on choosing checks.

## Units and documentation

- [0001-configuration](docs/0001-configuration.md)
- [0002-notification-gate](docs/0002-notification-gate.md)
- [0003-dashboard-ui](docs/0003-dashboard-ui.md)
- [0004-integration-responsive](docs/0004-integration-responsive.md)
- [0005-observation-reconciliation](docs/0005-observation-reconciliation.md)
- [0006-browser-toast-suppression](docs/0006-browser-toast-suppression.md)
- [0006a-clone-payload-safety](docs/0006a-clone-payload-safety.md)
- [0006b-dashboard-suppression-causes](docs/0006b-dashboard-suppression-causes.md)

## Tests

Regression tests are embedded in their patches at upstream test paths; the manifest lists each file. This keeps tests versioned with the code under test and runnable by upstream tooling. See the top-level validation and upgrade guides. No separate copied test suite can drift from the replayed tree.
