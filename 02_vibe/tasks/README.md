# Worker Task Packets

## 用途

`02_vibe/tasks/` 存放 M 生成的 worker task packet。

每个 task packet 都应能交给一个干净 worker session 独立执行。

## 规则

- 一个任务一个文件。
- 文件名使用 `ROLE-TASK-NAME-SEQ.md`。
- 任务文件必须写明 worker 角色、必读上下文、任务范围、允许/禁止动作、输出路径和结果格式。
- 任务文件必须指定唯一 result 路径。
- 已完成或已 covered 的任务文件不应再次派发。
- worker 默认不保留跨任务 session。
- task packet 本身不是项目事实，只是执行指令。

## 示例

```text
I-UPLOAD-BACKEND-PLAN-01.md
P-UI-V2-SPEC-01.md
Q-GEMINI-UX-RISK-01.md
```
