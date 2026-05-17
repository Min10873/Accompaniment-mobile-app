# Memory Protocol

## 目标

区分当前事实、历史过程和学习记录，避免文档互相覆盖或冲突。

## 三类信息

| 类型 | 放置位置 | 说明 |
|---|---|---|
| 原始输入 | `00_inbox/` | W 的原文，不改写 |
| 当前事实 | `01_context/` | 当前有效结论和状态 |
| 协作规则 | `02_vibe/` | agent、session、task、memory、trace 协议 |
| 产品事实 | `03_product/` | MVP、需求、路线 |
| 技术事实 | `04_architecture/` | 技术栈、系统设计、部署设计 |
| 测试事实 | `05_testing/` | 测试策略和验证清单 |
| 过程记录 | `07_traces/` | 给女儿看的协作过程 |
| 历史材料 | `99_archive/` | 旧输出、旧问题、过期材料 |

## 写入标准

只有满足以下条件才写入当前事实：

- W 明确确认。
- 对后续任务有持续影响。
- 不是临时想法。
- 不与更高优先级事实冲突。

## 冲突优先级

从高到低：

1. W 最新明确输入。
2. `01_context/current_state.md`
3. `01_context/user_answers.md`
4. `02_vibe/*_protocol.md`
5. 产品、架构、测试当前文档
6. 旧目录和归档材料

## context 与 memory 边界

- `01_context/` 记录当前项目事实。
- `02_vibe/memory_protocol.md` 记录记忆规则。
- 旧 `memory/` 目录只作为历史参考，后续不继续扩展为主事实源。

## 更新规则

- 当前事实变化时，优先更新 `01_context/current_state.md`。
- W 的回答变化时，更新 `01_context/user_answers.md`。
- 决策过程需要教学价值时，写入 `07_traces/decisions/`。
- 过期问题和旧总结进入 `99_archive/`，不作为当前事实读取。

