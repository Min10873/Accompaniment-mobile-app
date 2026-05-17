# Port Registry

## 目标

伴奏应用统一使用 `7000-7999` 端口段，避免和本机其他项目、系统服务、VPN/x-ui/xray 混在一起。

## 标准端口

| 场景 | 服务 | 端口 | 说明 |
|---|---|---:|---|
| local real | sidecar | `127.0.0.1:7000` | 抖音下载 sidecar |
| local real | backend + frontend | `127.0.0.1:7001` | 完整后端，`ACCOMPANIMENT_MOCK_PROCESSING=false` |
| local temporary | mock backend + frontend | `127.0.0.1:7011` | 只允许短时 UI/契约调试，用后关闭 |
| production target | sidecar | `127.0.0.1:7000` | 下一次生产端口迁移目标 |
| production target | backend | `127.0.0.1:7001` | 下一次生产端口迁移目标 |

## 当前生产事实

截至 2026-05-18，线上仍运行在旧端口：

| 服务 | 当前端口 |
|---|---:|
| sidecar | `127.0.0.1:8000` |
| backend | `127.0.0.1:8001` |

生产端口迁移必须单独执行并验收，不能只改文档就视为完成。

## 使用规则

- 给 W 本机测试链接前，必须确认 `/api/health` 返回 `processing_mode="real"`。
- 本机不同时保留旧 mock 后端和 real 后端，避免误测。
- 新增本项目服务时优先使用 `7002-7099`。
- `7100-7999` 暂留给后续批处理、队列、观测或临时调试。
- 公网入口仍由反向代理管理，不直接暴露内部端口。
