# Validation record

Baseline: `f6f6e6da26a29176ae0a2c928f507674eb593f66` (official upstream).
Reference: merged fork master `7162f0d0fac3bf51b31fdfcab4bc3f2f285958c6`.
Original exact-fork tree: `be13476ed780b6bf0eb5b129023f504a226102b3`.
Corrected default output tree: `e843c85f2cf45c151abb07fd27ae37fc9ea3d004`.
Corrected dependency-only output tree: `65031de845330b4858e305f87e35a6fb51e0b3e8`.

Local verification on November 9, 2026 (America/New_York), macOS arm64, Node 26.5.0, Docker Engine 29.9.2:

| Check | Evidence |
| --- | --- |
| Clean official-source replay | PASS, all seven before/after tree checkpoints and exact final fork tree |
| Local-source replay | PASS, independent object store, source worktree unchanged |
| Overlay failure-safety tests | 13 passed; corruption, conflicts, wrong pin/tree, missing dependencies/cycles, existing symlink/destination and path escape |
| Fresh lockfile installation | PASS, npm ci, 1196 packages; native dependencies installed |
| Production build | PASS on full replay with freshly installed dependencies |
| Full feature regression set | 59 passed, zero failures/skips; includes live delivery/restarts, Socket.IO and MariaDB migrations |
| Dependency-only selection | Corrected tree verified; production build and 20 Socket.IO/frontend checks passed (dependency directory reused from fresh lockfile install). |
| Recovery-only selection | Correctly rejected before checkout creation: explicit monitor-dependencies requirement |
| Lint | PASS, zero errors; 84 existing JS warnings and Stylelint deprecated-rule warnings |
| Full backend/container suite on exact-fork tree | 662 tests: 660 passed, 1 failed (MQTT container startup port timeout), 1 platform skip. The failed MQTT case passed when rerun on the corrected tree; no assertion or timeout was weakened. |
| Original exact-fork Chromium suite | 64 passed, 1 failed: clone save tried to persist derived dependencyActive as a DB column. Documented correction 0006a added. |
| Corrected full Chromium suite | 65 passed, zero failures (4.1 minutes), including the previously failing clone scenario |
| Original-reference reconstruction | PASS: alternate-index reversal of declared 0006a correction reproduces original fork tree exactly; actual changed-file set equals the two-file manifest allowlist |
| Validation-driver replay | PASS against official upstream using fresh-installed dependencies: exact replay, build and 59 feature tests; corrected replay also passes all 59 feature tests |

The first runner attempt tried integration tests before building `dist` and with Docker stopped: 56 passed and 3 failed (two server readiness timeouts, one missing runtime). The runner was corrected to build before tests and Docker was started. The corrected feature run above passed all 59 without skips. This was a harness/precondition failure, not a reason to modify application patches or their baseline.

Fresh installs still report upstream dependency deprecations and the uncovered optional fsevents install-script policy warning. These are inherited baseline conditions. No package, lockfile, authentication workaround or unrelated feature was silently added. Current official master is newer and is **not** validated by these results; see provenance.md. Linux hosted CI is configured to validate both module selections using fresh installs and all suites: [Actions](https://github.com/bamirian-capbloom/uptime-kuma-overlay/actions). The final corrected-head run is pending publication of this validation record; hosted status must be checked separately. CI failure must be resolved or explicitly reported, never treated as a green release. No production deployment, database upgrade, image publication or automatic merge was performed.

The only corrected-vs-fork tree difference is two production sanitation entries in server/server.js and five regression-test lines in test-monitor-dependency-socket.ts (7 insertions total), verified by a full Git diff against the merged fork commit. No original patch bytes were rewritten.

The complete backend run was on the exact-fork tree before the two-line clone sanitation correction; all 59 feature regressions, lint/build, complete 65-test browser suite and the isolated MQTT retry were then verified on the corrected tree. This is not claimed as a single all-green local full-backend run on the corrected tree. Hosted CI runs the full command on that final tree. Build warnings include existing bundle-size, Sass and browser-externalized-module notices. Browser snapshot restoration logs existing monitor cleanup/database errors even in the successful full suite; inspect reports instead of treating green assertions as a log-cleanliness guarantee. The original application checkout remained unchanged.

Hosted preflight qualification: the initial `ubuntu-latest` run passed replay/build/feature tests and the non-container backend phase, but every HiveMQ 2023.5 test failed because the inherited broker image exited before its startup log. No application assertions were changed. The workflow now pins Ubuntu 22.04, matching the pinned official backend workflow, and checks broker startup with captured logs before spending time on full validation. Results on other Linux runner images are not claimed.
