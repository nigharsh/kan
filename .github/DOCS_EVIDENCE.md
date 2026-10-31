# Documentation evidence requests

`docs-evidence.yml` runs on opened/updated/reopened/ready pull requests. A manual dispatch can inspect an existing PR number after this workflow is on the default branch.

The workflow reads the current PR head and the complete changed-file list, then uploads `docs-refresh-request.json`. It maps board/card/checklist changes to documentation workflows and records the requested ContextQA Max runner. No ContextQA token or Kan login is stored in GitHub for this request-only stage.

A successful GitHub check means **the capture request was prepared**, not that documentation was generated or verified. The workflow does not execute ContextQA, publish screenshots, start a paid run or change a test environment. Fork PRs receive no ContextQA credentials.

## Completing a request

1. Resolve the requested Max runner against the actual ContextQA tenant; do not relabel another mode as Max.
2. Confirm a deployed revision matches `head_sha`. The shared `kan-qa.vercel.app` URL by itself does not prove this. The mapper rejects a mismatched `--deployed-sha` if supplied.
3. Run the affected saved workflow using the authorized Kan test account/auth profile and per-case screenshots/video capture.
4. Collect selected results into [ContextQA Docs Evidence](https://github.com/contextqaai/contextqa-docs-evidence), privately retrieve and inspect media, add capture labels/callouts, and export a reviewed guide.
5. Compare against a reviewed baseline and approve the documentation update. Neither a passing test nor a new media hash alone establishes a meaningful documentation change.

The mapper is copied from `contextqa-docs-evidence/integrations/kan/docs_request.py`; keep them synchronized. Relevant application UI changes may require updating its path rules. Unknown backend changes are not automatically understood as business workflow changes.

## Observed check

PR #18 at `a0d0587a5f1fe13c0c132e235c6c7148825c2fe5` mapped to `kan-create-card` and `kan-checklist`. This was a local request-generation check against live GitHub metadata, not a deployment or capture claim.
