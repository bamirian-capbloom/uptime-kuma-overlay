# toast-lifecycle

Dismisses a monitor’s tracked DOWN toasts when its newest accepted observation becomes UP (PR #7). No timeout or global toast settings change.

Requires `monitor-dependencies`: the tracker and accepted observation machinery currently live there. Independently disable recovery by selecting only monitor-dependencies; recovery alone is deliberately rejected.

## Units and documentation

- [0007-recovery-cleanup](docs/0007-recovery-cleanup.md)

## Tests

Regression tests are embedded in their patches at upstream test paths; the manifest lists each file. This keeps tests versioned with the code under test and runnable by upstream tooling. See the top-level validation and upgrade guides. No separate copied test suite can drift from the replayed tree.
