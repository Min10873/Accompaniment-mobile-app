# Session Trace: Vibe Coding 环境与 MVP 收敛

## 目标

先搭建适合 W 的 vibe coding 环境，再确定伴奏应用的首版 MVP。

## 人的输入

W 提供了真实场景：

- 父母参加老年活动，经常需要伴奏。
- 当前人工流程是找抖音/YouTube、下载视频、ffmpeg 提取音频、微信发送。
- 希望父母可用，也可以推荐朋友用。
- 希望记录制作过程，给学 SC 的女儿参考。
- 有一台 Debian 12 VM，可作为服务端。
- 首版视频来源先做抖音。
- 首版先不做变调。

## M 的理解

M 判断：

- 这不是普通手机 App，核心是伴奏处理工作流。
- 父母需要简单入口，适合手机网页或快捷方式。
- 下载和 ffmpeg 处理不适合放手机端，适合放服务器。
- 女儿需求应作为学习记录系统，而不是混入伴奏业务功能。

## 任务拆解

| 子任务 | Owner | 输出 | 完成标准 |
|---|---|---|---|
| 定义 agent 体系 | M | `agents/`、`workflows/` | 角色和流程清晰 |
| 定义上下文和记忆 | M | `memory/` | agent 知道读写规则 |
| 收敛 MVP | Product-Architecture | `specs/mvp_v1.md` | 输入、流程、边界明确 |
| 决定技术栈 | Product-Architecture | `environment/tech_stack_decision.md` | 可本地开发，可部署 VM |
| 定义学习记录 | M | `specs/daughter_learning_trace.md` | 女儿需求有独立实现路径 |

## 执行过程

| 步骤 | 动作 | 产物 |
|---|---|---|
| 1 | 读取 W 的场景描述 | `context/project.md` |
| 2 | 追问环境和产品关键问题 | `environment/questions_for_w_round*.md` |
| 3 | 收敛 MVP V1 | `specs/mvp_v1.md` |
| 4 | 收敛技术栈 | `environment/tech_stack_decision.md` |
| 5 | 定义学习记录机制 | `specs/daughter_learning_trace.md` |

## 关键决策

| 决策 | 原因 | 影响 |
|---|---|---|
| 先做手机 Web/PWA | 父母和朋友容易访问 | 暂不开发原生 App |
| 后端用 Python FastAPI | 适合调用下载工具和 ffmpeg | 工程简单，便于部署 |
| 首版只做抖音分享链接 | 范围可控 | 不做自动搜索 |
| 首版不做变调 | 先完成主闭环 | rubberband 放后续版本 |
| 女儿需求做 learning trace | 避免干扰业务功能 | 开发过程可教学、可复盘 |

## 验证

当前验证为文档级验证：

- MVP 输入、输出、边界已明确。
- 技术栈与 VM 条件匹配。
- 部署前仍需确认 VM 访问、域名、端口和文件保留策略。

## 结果

已完成：

- 多 agent 体系。
- 上下文和记忆体系。
- MVP V1。
- 技术栈 V1。
- 女儿学习记录方案。

## 给女儿看的解释

这一步体现的是“先定义问题，再选择技术”。

软件开发不是一上来写代码，而是先弄清楚谁用、解决什么痛点、第一版只做什么、不做什么。agent 的作用不是替人拍脑袋，而是帮助人把模糊想法变成可执行计划。

