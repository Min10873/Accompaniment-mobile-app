# Worker Task: I-UPLOAD-BACKEND-PLAN-01

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
```

## Task

Task ID: `I-UPLOAD-BACKEND-PLAN-01`

Goal:

Design the smallest backend implementation plan for audio upload that reuses the current task/result/pitch flow.

## Context

Current product direction:

- Page 1 has two ways to get audio:
  - From Douyin link/share text.
  - Upload an existing audio file.
- Page 2 uses the current audio:
  - Play.
  - Download.
  - Copy link.
  - Pitch shift.

Upload draft scope:

- Single file upload.
- Supported formats: `mp3`, `m4a`, `wav`.
- Size limit: `20MB`.
- Retention: 7 days.
- Uploaded audio should enter the same result page.
- Uploaded audio should support play/download/copy link/pitch.

Current M decisions:

- UI wording should use `智能伴奏台`、`专业伴奏控制台`、`高品质伴奏提取`, not `发烧级`、`Hi-Res`、`无损`、`AI算法`.
- Backend may keep pitch semitone `1-11`, but parent UI defaults to `1-5`.

## Extra Context Files

```text
app/backend/app/main.py
app/backend/app/models.py
app/backend/app/task_store.py
app/backend/app/worker.py
app/backend/tests/test_api_contract.py
app/backend/tests/test_task_store.py
app/backend/tests/test_worker_real.py
```

## Scope

Read-only implementation planning.

Plan the backend API and internal changes. Do not implement them yet.

## Special Allowed

None; follow BOOT defaults.

## Special Forbidden

- Do not modify files.
- Do not implement upload.
- Do not install dependencies.
- Do not start services.
- Do not operate remote servers.
- Do not change product scope.

## Output

Write result to:

```text
02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md
```

## Output Focus

Return `I-R` with:

- Proposed endpoint contract, probably `POST /api/uploads`.
- Request/response shape.
- Storage and filename strategy.
- How to create `TaskRecord` and original `AudioVariant`.
- File type validation.
- 20MB validation.
- How upload tasks interact with existing `has_active_task()` / `SERVER_BUSY` behavior.
- Whether backend should return `expires_at` per audio variant.
- Test cases to add.
- Files that would need modification in implementation phase.
- Rollout risks.

## Done Criteria

M can ask W for confirmation and then implement safely.

## Stop Condition

Stop after writing `02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md`.

## Status

Done / covered by worker result. Do not dispatch this task again.

```text
02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md
```

## Result Format

```text
I-R:

结论：
- ...

实现/技术建议：
- ...

API 契约草案：
- ...

需要修改的文件：
- ...

测试计划：
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
