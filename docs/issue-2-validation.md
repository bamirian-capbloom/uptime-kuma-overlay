# Issue #2 validation and test-image record

Branch: feature/dashboard-suppression-causes. Implements dashboard issue #2 only; monitor-details issue #3 remains open. No merge is authorized until the user tests the branch container and approves.

## Local implementation checks

- The three new browser scenarios plus six setup checks pass (9 passed). Covers direct/indirect blocker changes, named links, expandable paths, actual DOWN counts, recovery, configuration edits, pause/deletion, disconnect/reconnect, stale history, and escaped long names in dark mobile RTL layout.
- Desktop and 390px dark RTL screenshots were visually inspected; the summary remains within the viewport and the path can be expanded with the keyboard.
- Focused ESLint and Stylelint checks for the new component/test pass with no new warnings. Full lint passes with zero errors and the 84 inherited warnings/deprecated Stylelint rules.
- All 18 overlay safety tests and both fresh module selections pass, including exact reconstruction of the original fork reference. The 59 existing feature regressions pass without skips. The production build passes.
- The new test harness initially navigated before login completed and initially omitted the existing pause confirmation dialog. Both harness steps were corrected; no application behavior was changed to accommodate them.
- The existing dependency browser test now checks the explanatory summary and one sidebar badge rather than the old duplicated summary badge.

## Required completion checks

Fresh replay must validate both module selections and the exact reference reconstruction. Run safety tests, feature regressions, full browser suite, production build and lint, and inspect hosted CI for the final branch head. Additional results and the branch test-container location/image/data provenance will be recorded before handoff.

## Container/data scope

The branch test container will be separate from existing ports 3005/3006, with a consistent copy of the current configured test volume. Test copies must not send duplicate external notifications. Keep the current volume and a recoverable pre-copy archive intact. The image must label the branch overlay revision and separately document the existing local authentication startup/schema patch (issue #12); that compatibility patch remains outside the maintained overlay manifests and this UI implementation.
