# Task Protocol

## 目标

让每个任务都有边界、owner、输出和完成标准。

## 标准任务格式

```text
Task ID:
Owner:
Goal:
Input:
Scope:
Out of Scope:
Files:
Output:
Done Criteria:
Risk:
```

## Worker Task Packet 模式

多 agent 协作默认采用无状态 worker task packet：

- M 是长期主控，保留项目上下文、决策状态和整合职责。
- P/I/Q worker 默认不保留跨任务 session。
- W 每次给 worker 派活时，使用一个干净 session。
- M 把 worker 身份、必读上下文、任务、权限、输出格式和结果路径写入一个任务文件。
- W 把任务文件交给对应 worker/model。
- worker 把结果写到指定 result 文件。
- W 告诉 M 哪个 result 文件已返回。
- M 读取 result，整合冲突、风险和待确认项。
- worker 输出不是项目事实，只有 W 确认后才成为事实。
- result 路径必须由 task packet 明确指定。
- worker 不得覆盖已经存在的 result 文件；如果指定 result 已存在，worker 必须停止并报告冲突。
- 已标记完成或 covered 的 task packet 不应再次派发；需要继续推进时，M 应创建新的 task id。

目录：

```text
02_vibe/tasks/
02_vibe/results/
```

命名：

```text
02_vibe/tasks/I-UPLOAD-BACKEND-PLAN-01.md
02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md
```

任务文件必须包含：

- Worker Role。
- Read First。
- Task ID 和 Goal。
- Context。
- Scope。
- Special Allowed / Special Forbidden。
- Output result file path。
- Result overwrite policy。
- Output Focus。
- Done Criteria。
- Stop Condition。
- Result Format。

## Owner

| Owner | 职责 |
|---|---|
| M | 理解、拆解、调度、验收、记忆和 trace |
| Product-Architecture | MVP、需求、架构边界、技术风险 |
| Implementation | 环境、代码、脚本、调试 |
| QA-Delivery | 验证、风险、交付说明 |

## 小动作

满足全部条件才算小动作：

- 文件数量不超过 3 个。
- 不移动或删除文件。
- 不写代码工程。
- 不安装依赖。
- 不启动服务。
- 不操作服务器。
- 结果可通过删除新增文件或回退少量修改恢复。

## 大动作

任何一项满足即为大动作：

- 创建应用代码工程。
- 移动或删除目录/文件。
- 合并大量文档。
- 修改超过 3 个文件。
- 运行安装、部署、服务启动命令。
- 访问或修改远程服务器。
- 引入新的技术栈或依赖。

## 执行规则

- 小动作：W 明确要求“继续/执行/写入”时可以做。
- 大动作：必须先给计划，等 W 明确确认。
- 任务完成后，应更新当前状态或 trace；如果这会超过 3 个文件，延后到下一步。

## 完成汇报

完成后按以下格式汇报：

```text
已完成：
- ...

修改文件：
- ...

未执行：
- ...

下一步：
- ...
```
