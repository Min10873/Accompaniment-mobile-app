# Worker Task: Q-TABBED-IA-VALIDATE-01

## Recommended Model Level

Use `gemini flash`.

Reason: this is a bounded QA validation task for mobile UI structure and regression checks.

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

Task ID: `Q-TABBED-IA-VALIDATE-01`

Goal:

Validate the new parent-facing information architecture:

- Page 1 and Page 2 are separated.
- Page 1 has two tabs: `抖音链接` and `上传音频`.
- Page 2 has two tabs: `播放保存` and `变调处理`.
- The duplicated `原调` display is removed when only one audio variant exists.
- Parent-facing mobile usability remains acceptable.

## Scope

QA only.

You may run local checks and use Playwright if available. The expected local real URL is:

```text
http://127.0.0.1:7001/
```

The sidecar should be on:

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
2. Page 1 checks:
   - initial page shows `抖音链接` tab active
   - `上传音频` tab switches without showing the Douyin textarea
   - tabs are large enough for mobile use
3. Page 2 checks:
   - submitting/uploading moves to Page 2 and hides Page 1
   - `播放保存` tab contains player/download/copy/valid-until
   - `变调处理` tab contains pitch controls
   - only one `原调` is visible when only original variant exists
   - semitone choices shown to parent user are 1-5
4. Regression:
   - `返回首页` returns to Page 1
   - upload flow still reaches result page
   - no obvious mobile overflow on iPhone SE width

## Output

Write result to:

```text
02_vibe/results/Q-TABBED-IA-VALIDATE-01.result.md
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
- QA result clearly says whether the tabbed IA is acceptable for W to test.
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
