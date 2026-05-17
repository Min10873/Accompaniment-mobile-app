# Agent 上下文与记忆体系 V1

## 核心结构

- `Global Context`：所有 agent 都能读的全局背景。
- `Project Context`：当前手机应用项目背景。
- `Task Context`：Main Agent 为单次任务生成的执行上下文。
- `Agent Context`：每类 agent 的职责和边界。
- `Runtime Context`：一次执行中的临时状态。

## 记忆类型

- `Profile Memory`：W 的稳定偏好和约束。
- `Project Memory`：项目长期事实。
- `Decision Memory`：已确认决策。
- `Task Memory`：任务状态。
- `Pattern Memory`：可复用工作模式。

## 核心规则

- Main Agent 负责读全局、写记忆、控质量。
- Worker Agent 只读必要上下文，只产出执行结果。
- 当前用户请求优先于历史记忆。
- 长期记忆只记录稳定事实和明确决策。
- 结果进入记忆前必须经过 Main Agent 判断。

## 当前状态

上下文与记忆体系 V1 已建立，可支撑后续 MVP 定义、任务拆解和多 agent 执行。

