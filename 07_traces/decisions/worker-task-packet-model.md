# Decision Trace: Worker Task Packet Model

## 决策

worker agent 默认采用无状态 task packet 模式。

M 保留长期上下文和整合职责。P/I/Q worker 每次任务使用干净 session。M 将任务写入 `02_vibe/tasks/`，worker 将结果写入 `02_vibe/results/`。

## 背景

项目开始时，P/I/Q 被设想为可复用 worker session。随着模型增多，W 同时有 `gemini flash`、`gemini pro` 和 `gpt 5.5` 等不同成本和能力的模型可用。

W 提出：模型和角色是正交关系，workerAgent 多次任务间不一定需要 session。更好的方式是每次 worker 执行都用干净 session，M 把初始化和任务写在一个文件里，W 直接把这个文件交给对应 worker。worker 返回时也写到 M 指定的文件里。

## 备选方案

| 方案 | 优点 | 风险 |
|---|---|---|
| 长期 worker session | worker 可以保留上下文，连续讨论方便 | 容易带入旧假设，输出格式漂移，未确认事实污染后续任务 |
| 每次手动粘贴 BOOT + TASK | 简单，不需要新目录 | 人工复制易漏上下文，任务和结果难追踪 |
| 无状态 task packet + result file | 上下文可控，任务可审查，结果可追踪，适合多模型并行 | 任务文件需要写得更完整 |

## 最终选择

采用无状态 task packet + result file。

目录：

```text
02_vibe/tasks/
02_vibe/results/
```

任务文件包含：

- Worker Role。
- Read First。
- Task ID 和 Goal。
- Context。
- Scope。
- Special Allowed / Special Forbidden。
- Output result file path。
- Output Focus。
- Done Criteria。
- Stop Condition。
- Result Format。

## 原因

这个项目里，M 才是长期主控。worker 的价值是完成一个边界清楚的任务，而不是积累长期记忆。

无状态 worker 更适合当前协作方式：

- 便于 W 把同一个任务交给不同模型。
- 避免 worker 把上一轮未确认结论带入下一轮。
- 方便把任务和结果都留在仓库中，支持复盘。
- 让女儿能看到每个 worker 是如何接任务、产出结果、被 M 整合的。

## 影响

- M 后续派活时优先创建 `02_vibe/tasks/*.md`。
- W 给 worker 的材料不再是散乱对话，而是完整任务文件。
- worker 结果写入 `02_vibe/results/*.result.md`。
- W 告诉 M 哪个 result 文件已返回。
- M 读取结果并整合；worker 输出仍不是项目事实。
- 只有 W 确认后，M 才把结论写入 `01_context/`、`03_product/`、`04_architecture/`、`05_testing/` 或 `07_traces/`。

## 给女儿看的解释

这体现了一个重要的软件工程思想：把“人脑记忆”变成“文件协议”。

如果 worker 长期聊天，它可能记住一些上次任务的假设。但这些假设不一定被 W 确认，也不一定适合下一次任务。无状态 task packet 的做法，是每次都把任务边界、上下文和输出要求写清楚，让 worker 像执行一张工单。

这类似真实工程里的 issue、ticket、pull request 和 CI 报告：

- issue 说明要做什么。
- worker 执行任务。
- result 文件说明做了什么。
- reviewer 决定是否接受。

这样协作更慢一点，但更可控、更适合多人和多模型长期合作。
