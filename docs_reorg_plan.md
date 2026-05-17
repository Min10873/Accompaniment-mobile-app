# 文档目录治理方案

## 目标

先解决“文档失控”问题，再继续开发。

本方案只定义整理规则，不直接移动文件。

## 当前问题

| 问题 | 表现 | 风险 |
|---|---|---|
| 目录边界不清 | `outputs/`、`environment/`、`specs/` 都在放决策和总结 | 后续找不到当前事实 |
| 问题文件分散 | `questions_for_w_round*.md` 越来越多 | 答案无法沉淀 |
| context 和 memory 重复 | 两边都记录项目事实 | agent 读取时容易冲突 |
| outputs 语义过宽 | 理解、决策、总结都放进去 | 长期维护困难 |
| trace 与 specs 混杂 | 女儿学习材料既在 specs，又在 traces | 教学线不清晰 |
| 缺少当前状态索引 | 不知道哪个文件是最新结论 | session 初始化困难 |

## 推荐新目录

```text
00_inbox/
  thinks/                 # W 的原始输入，保留原样

01_context/
  story.md                # 项目背景
  project.md              # 当前项目事实
  user_answers.md         # W 的回答汇总
  current_state.md        # 当前阶段和下一步

02_vibe/
  agents.md               # M 和 worker 角色
  session_protocol.md     # session 初始化规则
  memory_protocol.md      # 记忆规则
  trace_protocol.md       # learning trace 规则
  task_protocol.md        # 任务确认和执行规则

03_product/
  mvp_v1.md
  requirements.md
  roadmap.md

04_architecture/
  tech_stack.md
  system_design.md
  deployment_design.md

05_testing/
  test_strategy.md
  validation_checklist.md

06_delivery/
  runbook.md
  release_notes.md

07_traces/
  sessions/
  decisions/
  tutorials/
  templates/

99_archive/
  old_outputs/
  old_questions/
```

## 文件迁移映射

| 当前文件/目录 | 建议去向 | 处理方式 |
|---|---|---|
| `thinks/*` | `00_inbox/thinks/` | 移动，保留原文 |
| `context/story.md` | `01_context/story.md` | 移动 |
| `context/project.md` | `01_context/project.md` | 移动 |
| `environment/questions_for_w*.md` | `99_archive/old_questions/` | 归档，答案汇总到 `01_context/user_answers.md` |
| `agents/main_agent.md` + `agents/worker_agents.md` | `02_vibe/agents.md` | 合并 |
| `memory/*` | `02_vibe/memory_protocol.md` + `01_context/current_state.md` | 精简合并 |
| `workflows/multi_agent_flow.md` | `02_vibe/task_protocol.md` | 合并 |
| `specs/daughter_learning_trace.md` | `02_vibe/trace_protocol.md` | 合并 |
| `specs/mvp_v1.md` | `03_product/mvp_v1.md` | 移动 |
| `environment/tech_stack_decision.md` | `04_architecture/tech_stack.md` | 移动 |
| `environment/validation_checklist.md` | `05_testing/validation_checklist.md` | 移动 |
| `traces/*` | `07_traces/` | 移动 |
| `outputs/*` | `99_archive/old_outputs/` | 归档，必要结论合并到新目录 |

## 保留原则

- `00_inbox/` 只放原始输入，不改写。
- `01_context/` 只放当前事实。
- `02_vibe/` 只放 agent 协作规则。
- `03_product/` 只放产品范围和需求。
- `04_architecture/` 只放技术设计。
- `05_testing/` 只放验证策略。
- `07_traces/` 只放过程记录和教学材料。
- `99_archive/` 只放历史材料，不作为当前事实读取。

## 执行顺序

1. 新建目标目录。
2. 先复制，不删除旧文件。
3. 生成 `01_context/current_state.md`。
4. 生成 `01_context/user_answers.md`。
5. 合并 `02_vibe/*` 协议文件。
6. 迁移产品、架构、测试文件。
7. 迁移 traces。
8. 检查新目录是否完整。
9. W 确认后，再决定是否归档旧目录。

## 回滚方式

第一阶段只复制和新增文件，不删除旧文件。

如果整理方向不对：

- 删除新目录即可。
- 原目录仍保持不变。

## Session 硬规则

以后 M 开始任何 session 前必须先执行：

```text
1. 读取 `02_vibe/session_protocol.md`
2. 读取 `01_context/current_state.md`
3. 判断本轮是否会改文件
4. 如果是大动作，先列计划，等 W 确认
```

## 大动作定义

以下动作必须先确认：

- 创建代码工程。
- 移动或删除文件。
- 大规模重写文档。
- 安装依赖。
- 启动服务。
- 操作远程服务器。
- 修改超过 3 个文件。

## 建议下一步

先确认本方案。

确认后，只执行第一小步：

```text
新建 00_inbox/ 到 07_traces/ 目录
不移动、不删除、不合并
```

