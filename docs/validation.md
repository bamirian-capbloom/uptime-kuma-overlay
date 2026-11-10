# Validation record

Baseline: `f6f6e6da26a29176ae0a2c928f507674eb593f66` (official upstream).
Reference: merged fork master `7162f0d0fac3bf51b31fdfcab4bc3f2f285958c6`.
Default output tree: `be13476ed780b6bf0eb5b129023f504a226102b3`.
Dependency-only output tree: `1ec2f50c9572d2741c50429e1d929f6ad02bc1f2`.

Initial verification on November 9, 2026 (America/New_York), macOS arm64, Node 26.5.0, Docker Engine 29.9.2:

| Check | Evidence |
| --- | --- |
| Clean official-source replay | PASS, all seven before/after tree checkpoints and exact final fork tree |
| Local-source replay | PASS, independent object store, source worktree unchanged |
| Overlay failure-safety tests | 11 passed; corruption, conflicts, wrong pin/tree, missing dependencies/cycles, existing symlink/destination and path escape |
| Fresh lockfile installation | PASS, npm ci, 1196 packages; native dependencies installed |
| Production build | PASS on full replay with freshly installed dependencies |
| Full feature regression set | 59 passed, zero failures/skips; includes live delivery/restarts, Socket.IO and MariaDB migrations |
| Dependency-only selection | Exact PR #6 tree, 19 frontend tests passed, build passed (reuses fresh full-replay dependency directory) |
| Recovery-only selection | Correctly rejected before checkout creation: explicit monitor-dependencies requirement |
| Lint | PASS, zero errors; 84 existing JS warnings and Stylelint deprecated-rule warnings |
| Full backend/container suite | Running; final evidence will be added before handoff |
| Full Chromium suite | Running; final evidence will be added before handoff |
| Final validation-driver replay | Running against official upstream using the freshly installed dependency directory |

The first runner attempt tried integration tests before building `dist` and with Docker stopped: 56 passed and 3 failed (two server readiness timeouts, one missing runtime). The runner was corrected to build before tests and Docker was started. The corrected feature run above passed all 59 without skips. This was a harness/precondition failure, not a reason to modify application patches or their baseline.

Fresh installs still report upstream dependency deprecations and the uncovered optional fsevents install-script policy warning. These are inherited baseline conditions. No package, lockfile, authentication workaround or unrelated feature was silently added. Current official master is newer and is **not** validated by these results; see provenance.md. Linux hosted CI separately validates both module selections using fresh installs and all suites. CI failure must be resolved or explicitly reported, never treated as a green release. No production deployment, database upgrade, image publication or automatic merge was performed.
