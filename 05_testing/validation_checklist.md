# Validation Checklist

## 目标

定义当前阶段到 MVP V1 的验证标准。

## Vibe Coding

- [x] `01_context/current_state.md` 存在。
- [x] `01_context/user_answers.md` 存在。
- [x] `02_vibe/README.md` 存在。
- [x] `02_vibe/agents.md` 存在。
- [x] `02_vibe/session_protocol.md` 存在。
- [x] `02_vibe/task_protocol.md` 存在。
- [x] `02_vibe/memory_protocol.md` 存在。
- [x] `02_vibe/trace_protocol.md` 存在。

## Product

- [x] MVP V1 已定义。
- [x] 用户已明确为父母和后续朋友。
- [x] V1 输入已明确为抖音分享文本。
- [x] V1 输出已明确为 HTTP 音频链接。
- [x] 当前可用版本已支持变调。

## Architecture

- [x] 技术栈已确认。
- [x] 前端形态已确认为手机 Web/PWA。
- [x] 后端已确认为 Python FastAPI。
- [x] 音频处理已确认为 ffmpeg。
- [x] 部署候选为 Debian 12 VM。

## Dev Runtime

- [x] 应用工程已创建。
- [x] 依赖可安装。
- [x] 后端可本地启动。
- [x] 前端页面可通过 `https://us.wumpus.top/` 打开。
- [x] 手机视口可查看。
- [x] ffmpeg 可执行。
- [x] 下载工具可处理抖音链接。

## MVP Functional

- [x] 页面可提交抖音分享文本。
- [x] 系统可提取抖音短链接。
- [x] 系统可下载抖音视频。
- [x] 系统可提取音频。
- [x] 系统可生成 HTTP 音频链接。
- [x] 音频链接可播放。
- [x] 音频文件保留 7 天。
- [x] 音频可下载。
- [x] 支持变调。
- [x] admin 入口存在并受 Basic Auth 保护。
- [x] 线上 `/api/health` 版本号已按事实记录为 `v0.1.9`。
- [x] 服务器闲时 Python 进程 CPU 占用约 45% 已定位到 sidecar 主进程。
- [x] sidecar 高 CPU 初步定位为 uvicorn `reload=True` 开发模式。
- [x] sidecar 闲时 CPU 占用已降到可接受水平。
- [x] 本地前端已新增明显的“粘贴链接”按钮和长按粘贴提示。
- [x] 粘贴体验改动已通过本地 Playwright 手机视口 mock 流程验证，截图 `/private/tmp/accompaniment-mobile-paste.png`。
- [x] 本地任务恢复/结果页面已新增“重新开始”按钮，并通过 Playwright 验证可清除 `?task=` 回到主页，截图 `/private/tmp/accompaniment-home-button.png`。
- [x] 本地成功页布局已调整并通过 Playwright 手机视口验证：返回首页在右上角，版本号在页尾，当前播放/下载与变调分区，半音说明可见，当前音频链接有效期显示为绝对日期。截图 `/private/tmp/accompaniment-result-layout.png`。
- [x] 本地后端已实现 `POST /api/uploads`：支持 `mp3/m4a/wav`、20MB 限制、上传成功创建 `done` 任务并复用现有结果和变调链路。
- [x] 上传后端测试已通过：`python3 -m pytest app/backend/tests -q`，结果 `45 passed`。
- [x] 前端上传入口已接入并通过手机视口冒烟验证，截图 `/private/tmp/accompaniment-upload-entry.png`。
- [x] Q 已完成上传前后端联调验证：有效上传、错误上传、结果页能力和回归检查通过，结果 `02_vibe/results/Q-UPLOAD-FRONTEND-VALIDATE-01.result.md`。
- [ ] 上传入口已发布并在真实手机端实测。
- [ ] 粘贴体验、返回首页和成功页布局改动已发布并在真实手机端实测。

## Learning Trace

- [x] learning trace 方案已定义。
- [x] trace 目录和模板已存在。
- [ ] 开发环境搭建阶段有 session trace。
- [x] 编码阶段有 session trace。
- [ ] 关键技术问题有 decision trace。

## Delivery

- [x] 运行说明存在。
- [x] 部署说明存在。
- [x] 已知限制存在。
- [x] W 可按说明运行或部署。
