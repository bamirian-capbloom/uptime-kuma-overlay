# Repository migration and ownership

Preferred home: `bamirian-capbloom/uptime-kuma-overlay`, separate from the application fork. The default branch initially contains only repository identity; the complete implementation is reviewed in a draft PR. Nothing changes official `louislam/uptime-kuma`, and no PR is automatically merged.

If repository creation is unavailable, preserve this directory as a self-contained `overlay/` subtree on a review branch of the user's fork. Its scripts locate manifests relative to themselves, so moving the whole directory does not break it. Open a draft PR against fork master; never send it upstream. Creating the separate home later requires account permission to create a repository, push branches, and enable Actions (token repo/workflow permissions for a classic PAT).

After review, move the complete directory to the standalone repository root, retain its manifest/checksums and provenance unchanged, run self-tests and full validation, then open a new draft PR. Update documentation/links in the old fork PR and archive only the redundant overlay branch after review. Do not rebase the application master or rewrite merged PR history. Use an independent clone when consuming the overlay; the source fork can remain a comparison reference until an upstream upgrade has separate evidence.
