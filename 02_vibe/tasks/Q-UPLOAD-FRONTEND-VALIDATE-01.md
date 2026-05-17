# Worker Task: Q-UPLOAD-FRONTEND-VALIDATE-01

## Recommended Model Level

Use `gemini flash`.

Reason: this is a bounded QA validation task with explicit checks and no product architecture decisions.

## Worker Role

You are Q, the QA-Delivery worker for this project.

Use a clean session. Do not rely on previous worker memory.

## Read First

```text
README.md
01_context/current_state.md
02_vibe/session_protocol.md
02_vibe/task_protocol.md
02_vibe/session_roles.md
03_product/product_design_v2.md
05_testing/validation_checklist.md
```

## Task

Task ID: `Q-UPLOAD-FRONTEND-VALIDATE-01`

Goal:

Validate the local upload-audio frontend and backend integration from a parent-user mobile perspective.

## Context

Recent implementation facts to verify:

- Backend endpoint: `POST /api/uploads`
- Request: `multipart/form-data`, field name `file`
- Supported formats: `mp3`, `m4a`, `wav`
- Size limit: `20MB`
- Upload success returns `201 Created`, `status=done`, `audio_url`, `audio_variants.original`, and `expires_at`
- Frontend home page now has a secondary entry: `上传手机里的音频`
- Upload success should enter the existing result page with:
  - native audio player
  - download action
  - copy link action
  - pitch controls
  - absolute valid-until date

## Scope

QA only.

You may run local tests, start a temporary local backend if needed, and use Playwright if available.

## Special Forbidden

- Do not modify project files.
- Do not operate remote servers.
- Do not install dependencies.
- Do not commit or push.
- Do not overwrite existing result files.
- Do not test with private real user audio unless W explicitly provides one.

## Suggested Checks

1. Static/API checks:
   - `python3 -m pytest app/backend/tests -q`
   - `node --check app/frontend/app.js`
2. Backend upload checks:
   - valid mp3 upload returns 201
   - unsupported extension returns 422
   - empty file returns 422
   - oversized file behavior is covered by tests
3. Mobile UI checks:
   - iPhone SE or similar narrow viewport
   - home page shows upload entry without hiding the Douyin entry
   - upload entry text is readable and touch target is large enough
   - successful upload reaches result page
   - result page still shows audio player, download, copy link, pitch area, and valid-until date
4. Regression checks:
   - Douyin paste flow UI is still present
   - return-home button still clears task view

## Output

Write result to:

```text
02_vibe/results/Q-UPLOAD-FRONTEND-VALIDATE-01.result.md
```

If this file already exists, stop and report a result-file collision. Do not overwrite it.

## Output Focus

Return `Q-R` with:

- Overall pass/fail.
- Exact commands/checks run.
- Screenshots created, if any.
- Findings ordered by severity.
- Mobile usability notes.
- Remaining risks.
- Files changed: should be `none`.
- Whether this is ready for W local/phone test.

## Done Criteria

- Result file exists at the specified path.
- QA result clearly says whether the local upload path is acceptable for W to test.
- Any blocker includes exact reproduction steps.

## Result Format

```text
Q-R:

结论：
- ...

验证结果：
- ...

发现的问题：
- ...

移动端可用性：
- ...

风险/阻塞：
- ...

需要 W 决策：
- ...

需要 M 整合：
- ...

本 session 未执行：
- ...
```
