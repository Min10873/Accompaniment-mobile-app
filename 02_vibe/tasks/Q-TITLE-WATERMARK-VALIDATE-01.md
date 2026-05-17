# Worker Task: Q-TITLE-WATERMARK-VALIDATE-01

## Recommended Model Level

Use `gemini flash`.

Reason: bounded QA validation for title display, download filename, and metadata watermark behavior.

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
04_architecture/port_registry.md
05_testing/validation_checklist.md
```

## Task

Task ID: `Q-TITLE-WATERMARK-VALIDATE-01`

Goal:

Validate the new song title and watermark behavior:

- Result page title uses `伴奏已准备好`, not `处理好了`.
- Page 2 displays the song title.
- Upload flow has a `歌曲名字` input.
- Choosing a file auto-fills song title from filename without extension.
- Upload sends the title to backend and `TaskResponse.title` returns it.
- Download filename is `歌曲名-版本-歌伴侣.后缀`.
- Audio metadata contains `comment=from LFAPP` for real generated/uploaded audio when ffmpeg can write metadata.

## Scope

QA only.

Expected local real URL:

```text
http://127.0.0.1:7001/
```

Sidecar:

```text
http://127.0.0.1:7000/
```

## Special Forbidden

- Do not modify project files.
- Do not operate remote servers.
- Do not install dependencies.
- Do not commit or push.
- Do not overwrite existing result files.

## Suggested Checks

1. Static checks:
   - `node --check app/frontend/app.js`
   - `python3 -m pytest app/backend/tests -q`
2. Upload/title checks:
   - choose `some-song.mp3`, confirm title input defaults to `some-song`
   - change title to a Chinese title, upload, confirm result page displays it
   - confirm `/api/tasks/{task_id}` includes `title`
3. Download filename checks:
   - original variant download name should be `歌曲名-原调-歌伴侣.mp3` or original extension
   - pitch variant download name should be `歌曲名-升高N半音-歌伴侣.mp3` / `歌曲名-降低N半音-歌伴侣.mp3`
4. Metadata checks:
   - use a valid small audio file
   - confirm resulting uploaded audio metadata includes `comment=from LFAPP`
   - if `ffprobe` is unavailable, use `ffmpeg -i file -f null -` and inspect metadata output

## Output

Write result to:

```text
02_vibe/results/Q-TITLE-WATERMARK-VALIDATE-01.result.md
```

If this file already exists, stop and report a result-file collision. Do not overwrite it.

## Output Focus

Return `Q-R` with:

- Overall pass/fail.
- Exact commands/checks run.
- Screenshots created, if any.
- Findings ordered by severity.
- Remaining risks.
- Files changed: should be `none`.
- Whether this is ready for W local/phone test.

## Done Criteria

- Result file exists at the specified path.
- QA result clearly says whether title/download/watermark behavior is acceptable.
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

风险/阻塞：
- ...

需要 W 决策：
- ...

需要 M 整合：
- ...

本 session 未执行：
- ...
```
