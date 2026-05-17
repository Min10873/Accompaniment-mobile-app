# Worker Results

## 用途

`02_vibe/results/` 存放 worker 按 task packet 要求写回的结果文件。

## 规则

- 一个任务对应一个结果文件。
- 文件名使用 `TASK-ID.result.md`。
- 结果必须使用对应角色格式：`P-R`、`I-R` 或 `Q-R`。
- result 文件不得被 worker 覆盖。
- 如果 task packet 指定的 result 文件已存在，worker 应停止并报告冲突。
- worker 结果不是项目事实。
- M 读取并整合结果后，仍需 W 确认才能写入长期项目状态。

## 示例

```text
I-UPLOAD-BACKEND-PLAN-01.result.md
P-UI-V2-SPEC-01.result.md
Q-GEMINI-UX-RISK-01.result.md
```
