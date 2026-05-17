# 多 Agent 体系 V1

## 核心定义

这是一个服务于 W 的 AI Native 手机应用开发体系。

主 agent 负责理解、拆解、调度、验收和对话；从 agent 负责具体执行。

## 角色结构

- W：目标提出者、最终决策者。
- Main Agent：对话入口、任务调度、质量把关。
- Product Agent：需求和验收。
- Architecture Agent：架构和边界。
- Implementation Agent：实现和调试。
- QA Agent：测试和风险。
- Delivery Agent：交付和说明。

## 工作流

```text
W
-> Main Agent
-> Product / Architecture / Implementation / QA / Delivery
-> Main Agent
-> W
```

## 第一阶段目标

先把协作体系跑通，再开发手机应用。

## 当前状态

已建立 V1 骨架，可进入 MVP 定义阶段。

