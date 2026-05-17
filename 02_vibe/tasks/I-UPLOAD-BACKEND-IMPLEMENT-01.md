# Worker Task: I-UPLOAD-BACKEND-IMPLEMENT-01

## Worker Role

You are I, the Implementation worker for this project.

Use a clean session. Do not rely on previous worker memory.

## Read First

```text
README.md
01_context/current_state.md
01_context/user_answers.md
02_vibe/session_protocol.md
02_vibe/task_protocol.md
02_vibe/session_roles.md
03_product/product_design_v2.md
04_architecture/system_design.md
02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md
```

## Task

Task ID: `I-UPLOAD-BACKEND-IMPLEMENT-01`

Goal:

Implement the smallest backend upload-audio endpoint that reuses the existing task/result/pitch flow.

## Context

Accepted implementation decisions:

- Endpoint: `POST /api/uploads`.
- Request: `multipart/form-data`, field name `file`.
- Supported formats: `mp3`, `m4a`, `wav`.
- Size limit: `20MB`.
- Retention: 7 days.
- Upload success directly creates a `done` task.
- Response status should be `201 Created`.
- Reuse existing `TaskRecord`.
- Create `audio_variants["original"]`.
- Uploaded audio should enter the same result page and existing pitch flow.
- Keep original file format in V1; do not transcode.
- Use random filename; do not preserve user original filename.
- Mark uploaded original variant with `source="upload"`.
- Backend should expose `expires_at` in task and/or audio variant responses so frontend does not need to infer validity only from `created_at + 7 days`.

## Extra Context Files

```text
app/backend/app/main.py
app/backend/app/models.py
app/backend/app/task_store.py
app/backend/app/worker.py
app/backend/app/config.py
app/backend/tests/test_api_contract.py
app/backend/tests/test_task_store.py
app/backend/tests/test_worker_real.py
```

## Scope

Implement backend only.

Do not change parent-facing frontend UI in this task.

## Special Allowed

You may modify only these files:

```text
app/backend/app/main.py
app/backend/app/models.py
app/backend/app/task_store.py
app/backend/app/config.py
app/backend/tests/test_api_contract.py
app/backend/tests/test_task_store.py
app/backend/tests/conftest.py
```

You may add a new backend helper file if it is clearly needed, for example:

```text
app/backend/app/uploads.py
app/backend/tests/test_uploads.py
```

You may run local backend tests, especially:

```text
python3 -m pytest app/backend/tests -q
```

## Special Forbidden

- Do not modify frontend files.
- Do not modify delivery scripts.
- Do not install dependencies.
- Do not start long-running services.
- Do not operate remote servers.
- Do not change sidecar behavior.
- Do not implement transcoding.
- Do not store original upload filenames in task records or API responses.
- Do not save files outside the configured app data/audio directories.
- Do not overwrite unrelated user or worker changes.

## Output

Write result to:

```text
02_vibe/results/I-UPLOAD-BACKEND-IMPLEMENT-01.result.md
```

If this file already exists, stop and report a result-file collision. Do not overwrite it.

## Output Focus

Return `I-R` with:

- Endpoint implemented and exact contract.
- Files changed.
- Validation behavior for:
  - missing file
  - empty file
  - unsupported extension/type
  - over 20MB
  - normal upload
- How `TaskRecord`, `TaskResponse`, and `AudioVariant` changed.
- How `expires_at` is returned.
- Test results.
- Known limitations.
- Any decisions M/W still need to make.

## Done Criteria

- `POST /api/uploads` exists.
- Valid upload returns `201 Created`, `status=done`, `audio_url`, and `audio_variants.original`.
- Uploaded file is saved under existing audio storage with random filename.
- Invalid uploads are rejected without leaving final audio/task records behind.
- Existing task and pitch tests still pass.
- New upload tests cover the main validation and happy paths.
- Result is written to `02_vibe/results/I-UPLOAD-BACKEND-IMPLEMENT-01.result.md`.

## Stop Condition

Stop after implementation, tests, and result file are complete.

## Result Format

```text
I-R:

结论：
- ...

实现/技术结果：
- ...

修改文件：
- ...

API 契约：
- ...

验证结果：
- ...

风险/阻塞：
- ...

需要 W 决策：
- ...

需要 M 整合：
- ...

Learning Trace 候选：
- ...

本 session 未执行：
- ...
```
