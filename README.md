# Uptime Kuma feature overlay

Portable, ordered customizations for the official Uptime Kuma source. This repository stores patches, integrity manifests, regression tests embedded in those patches, and operator documentation—not a second application fork. Nothing deploys or publishes images.

**Supported upstream:** `f6f6e6da26a29176ae0a2c928f507674eb593f66` only. Default replay exactly reproduces fork master after merged PRs #1–#7, `7162f0d0fac3bf51b31fdfcab4bc3f2f285958c6`. Current upstream master is newer; see [provenance and exclusions](docs/provenance.md). Read [validation results and limitations](docs/validation.md) before use. A draft is not a validated release.

| Feature | Behavior | Requires |
| --- | --- | --- |
| [monitor-dependencies](features/monitor-dependencies/README.md) | Configuration, durable alert suppression, indicators, browser DOWN toast suppression, tests | Pinned upstream |
| [toast-lifecycle](features/toast-lifecycle/README.md) | Dismiss a monitor's DOWN toasts on accepted UP | monitor-dependencies |

## Replay

Supported replay hosts: Linux and macOS. Requires Git, Python 3.9+, and an absent destination whose parent exists. Source may be an official upstream URL or a local clone containing the pinned object. The driver checks out the pin regardless of the source's current branch. It never patches an existing checkout.

```sh
python3 scripts/apply.py https://github.com/louislam/uptime-kuma.git ../kuma-custom
# Disable recovery cleanup, keeping dependency features:
python3 scripts/apply.py https://github.com/louislam/uptime-kuma.git ../kuma-dependencies --features monitor-dependencies
```

Validate using Node >=26.2, npm, Docker, and Chromium installed for the pinned Playwright version:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py https://github.com/louislam/uptime-kuma.git ../kuma-validation --full --install-browser
```

`validate.py` installs the lockfile, replays into an independent clone, verifies every Git tree, runs feature regressions (including MariaDB), and builds. `--full` also runs backend/container, lint and browser suites. `--install-browser` installs Chromium and OS dependencies before the browser phase; omit it when the correct browser is already cached. CI uses this option. Browser tests use disposable `data/playwright-test`; full backend tests need Docker and additional service images. The local `--reuse-dependencies PATH` shortcut is documented as weaker evidence than a fresh lockfile install.

See [architecture and extension contract](docs/architecture.md), [upgrade/rollback runbook](docs/operations.md), [migration plan](docs/migration.md), and the feature READMEs for every logical unit's documentation. Uptime Kuma patch content retains its upstream MIT license ([LICENSE](LICENSE)); overlay tooling is MIT-licensed as well.
