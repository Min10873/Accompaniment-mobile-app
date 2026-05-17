# Vibe Coding

## 目录定位

`02_vibe/` 是 agent 协作规则目录，只放长期有效的工作协议。

它不放产品需求、不放技术实现、不放历史过程。

## 文件说明

| 文件 | 用途 |
|---|---|
| `agents.md` | 定义 W、M、worker 的角色和边界 |
| `session_protocol.md` | 定义每次 session 如何启动、何时必须确认 |
| `task_protocol.md` | 定义任务格式、小动作/大动作和完成汇报 |
| `memory_protocol.md` | 定义当前事实、历史材料、过程记录的边界 |
| `trace_protocol.md` | 定义女儿 learning trace 如何记录 |
| `tasks/` | M 生成的无状态 worker task packet |
| `results/` | worker 返回的 result 文件 |

## M 的启动顺序

每次 session 开始时，M 必须先读：

1. `01_context/current_state.md`
2. `01_context/user_answers.md`
3. `02_vibe/session_protocol.md`
4. 与任务相关的协议或设计文件

涉及本地运行、联调、端口、发布或服务器时，还必须读：

```text
04_architecture/port_registry.md
```

## 当前硬规则

- 不经 W 确认，不做大动作。
- 大动作包括：创建代码工程、移动/删除文件、大规模重写文档、安装依赖、启动服务、操作服务器、一次修改超过 3 个文件。
- 文档迁移采用“复制后确认”，旧文件先不动。
- 当前阶段优先保证项目可控，再进入开发环境和编码。
- 伴奏应用端口段固定为 `7000-7999`：本地 real 使用 `7000/7001`，临时 mock 使用 `7011` 且用后关闭。
