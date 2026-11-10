# Provenance and divergence audit

Fork master verified after PR #7 merge: `7162f0d0fac3bf51b31fdfcab4bc3f2f285958c6`. Exact common ancestor with observed official master: `f6f6e6da26a29176ae0a2c928f507674eb593f66`. Official master observed: `b376409720f6df948707a3366398248d370bbf51`. This overlay targets the shared ancestor, not current upstream master. No claim of compatibility with any other SHA is made.

All seven first-parent fork changes correspond to merged PRs #1–#7. Each patch is the binary-safe full-index net diff from the preceding merge tree. There is no unrelated fork-only commit in that range; the original seven-unit replay was verified equal to the entire fork target tree `be13476ed780b6bf0eb5b129023f504a226102b3`. No lockfile, package or official workflow divergence is introduced. PR #4 includes shared Tooltip RTL positioning and Details URL wrapping discovered through dependency integration testing; these are explicitly retained related fixes, not hidden divergence.

Newer upstream commits deliberately excluded (a rebase requires validation):

```text
b3764097 fix: regression - incorrect uptime badge color in status pages (#8141)
c64c6d95 fix: update PM2 ecosystem config for v3 (#8139)
a004449f fix: better-auth 1.7.x and promisify-child-process regessions  (#8136)
1f47802e chore: fix nightly release tar import (#8135)
b92de594 chore: Update dependencies (#8101)
2b90632a chore: Translations Update from Weblate (#8100)
5915ab38 chore: replace sass with sass-embedded for faster frontend builds (#8128)
0cde0e72 Translated using Weblate (Portuguese (Brazil))
1e43f1f9 Translated using Weblate (Dutch)
c16190a9 Translated using Weblate (Ukrainian)
59f6d662 Translated using Weblate (French)
c4f983a4 fix: the dev frontend connection issue (#8123)
```

In particular upstream authentication/promisify-child-process fixes and dependency updates may affect fresh installation or browser startup. This overlay does not silently import the unmerged `fix/auth-schema-startup` fork branch. If the pinned baseline fails validation, record the failure and do not release or change the pin merely to get a clean patch apply. Upgrade as a separately reviewed change.

## Corrective delta discovered during validation

Exact-fork replay passed the feature subset but failed the existing full-browser clone scenario: derived `dependencyActive` from PR #5 reached generic DB import as a nonexistent column. Unit `0006a-clone-payload-safety` strips both display-only activity aliases before import and adds a Socket.IO regression. At the initial overlay release this was the sole intentional difference from fork master: `server/server.js` and `test/backend-test/test-monitor-dependency-socket.ts`. Initial output was `e843c85f2cf45c151abb07fd27ae37fc9ea3d004`; initial dependency-only output was `65031de845330b4858e305f87e35a6fb51e0b3e8`. Root `reference.tree` preserves original fork provenance; `intended.tree` pins the corrected target. For that initial release, full tree comparison to the original fork showed only those two files. The seven original patch files retain their original bytes/checksums; only the extra corrective unit and later tree checkpoints change.

## Issue #2: dashboard suppression explanations

Unit 0006b adds an explanatory private dashboard summary, current-blocker links and ordered dependency-path disclosures. Its source of truth is the existing observation resolver; no notification, API or schema behavior changes. The complete additional file inventory is in the module manifest and unit documentation. Root intended.difference_from_reference now lists the clone correction and this UI feature together; intended.correction_units is the reversible-additions ledger used to prove reconstruction of the original fork reference. No original PR patch bytes were rewritten.

Current intended default tree: `ca06b08c107c18b22b608898c578fbd665468518`. Current dependency-only tree: `b25e2330f283229f9f15193cf7ac1c7f8e7f4a5f`. Fresh replay must reproduce these trees, while reversing the declared additional units must still produce original fork reference `be13476ed780b6bf0eb5b129023f504a226102b3`. Container testing continues to apply the separately recorded local authentication compatibility patch; issue #12 tracks its integration or retirement, and it is not silently included in these overlay trees.
