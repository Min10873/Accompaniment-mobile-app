# Current State

## 当前阶段

当前版本已进入可用验收状态：公开 HTTPS 入口、父辈使用界面、admin 入口、抖音链接处理、变调和下载能力都已具备。下一阶段建议先固化版本、补齐验收记录和发布状态，再继续扩大产品范围。

## 当前原则

- 不经 W 确认，不做大动作。
- 大动作包括：创建代码工程、移动/删除文件、大规模重写文档、安装依赖、启动服务、操作服务器、一次修改超过 3 个文件。
- 当前阶段已完成复制式整理，删除旧文件前必须再次确认。

## 分工约定补充

- W 负责远程服务器上的所有操作。
- M 负责主控、拆解、调度、整合，也可直接执行本机工作区内的分析和小修改。
- I 负责本机工作区内的实现、脚本、调试和验证。
- Q 负责本机工作区内的验证、验收和风险检查。
- W 不默认负责本机打包、检查、修改或验证，除非该步骤必须由人手工完成。
- 涉及远程服务器的操作，由 W 执行，M 提供可审查步骤。

## 已确定

- M 是主 agent，负责对话、调度、验收、记忆和 vibe coding 环境。
- worker 合并为 3 类：Product-Architecture、Implementation、QA-Delivery。
- worker agent 协作模式已调整为无状态 task packet：M 生成 `02_vibe/tasks/*.md`，W 交给干净 worker session，worker 写回 `02_vibe/results/*.result.md`，M 再整合；详见 `07_traces/decisions/worker-task-packet-model.md`。
- 当前线上事实版本是 `v0.1.9`：公开 `/api/health` 在 2026-05-17 外部检查返回 `{"status":"ok","version":"v0.1.9","processing_mode":"real"}`。
- W 已在手机和 admin 上测试当前版本，认为这是一个不错的可用版本。
- MVP V1 当前能力是手机网页输入抖音分享文本，服务器下载视频并提取音频，返回 HTTP 音频链接，并支持变调和下载。
- 当前版本已具备 admin 入口和父辈使用界面。
- V1 成功页优先显示音频播放器，并提供复制链接按钮。
- V1 失败页只向老人展示人话错误，技术细节只保留在后台记录。
- V1 任务状态固定为 `queued`、`downloading`、`extracting`、`done`、`failed`、`expired`。
- V1 不使用数据库，用 JSON 任务记录和文件存储支撑 7 天保留。
- V1 不设置等待队列；已有任务处理中时，新提交直接返回服务忙。
- 测试1分享文本作为 MVP V1 首个真实 E2E 验收样本。
- 本机真实链路已通过：测试1分享文本 -> sidecar 下载 -> ffmpeg 提取 -> 任务 done -> MP3 可通过本机 HTTP 访问。
- 远程服务器真实链路已通过：抖音短链 -> sidecar 解析/下载 MP4 -> FastAPI 调 ffmpeg 提取 MP3 -> 任务 `done` -> MP3 可通过 HTTP 下载并播放。
- 多样本真实回归已完成：2-3 个真实抖音样本已用于验证短链解析、下载、ffmpeg 和 HTTP 音频服务稳定性。
- 历史已验证发布版本是 `v0.1.4`；当前线上运行时版本报告为 `v0.1.9`。
- 最小上线包流程已完成：`06_delivery/package_release.sh` 可生成版本化 tar.gz，`06_delivery/deploy.sh` 支持 deploy/start/stop/restart/status/rollback。
- `deploy.sh` 只管理 FastAPI，不管理 sidecar，不碰 VPN/x-ui/xray 或 80/443。
- `deploy.sh status` 已输出 `systemd_backend`、`systemd_backend_enabled`、`systemd_sidecar` 和 legacy pid 状态；运行态事实以 systemd 字段为准。
- `deploy.sh start/stop/restart/rollback` 仍是 legacy pid 模式，systemd 管理后不作为日常启停入口。
- 远程服务器当前以 real 模式运行：`ACCOMPANIMENT_MOCK_PROCESSING=false`，sidecar 地址为 `http://127.0.0.1:8000`。
- sidecar 使用 `Evil0ctal/Douyin_TikTok_Download_API`，绑定 `127.0.0.1:8000`；Cookie 属于私有配置，不进入仓库、trace 或对话。
- sidecar 已由 systemd 管理：`accompaniment-sidecar.service` 为 `active (running)`，已启用开机自启，`/docs` 和 `get_aweme_id` 轻量验证通过。
- 主 FastAPI 后端已由 systemd 管理：`accompaniment-backend.service` 为 `active (running)`，已启用开机自启，绑定 `127.0.0.1:8001`。
- 服务器重启恢复验收已通过：重启后 x-ui/VPN、sidecar、backend 均自动恢复，`/api/health` 返回 `{"status":"ok","processing_mode":"real"}`。
- sidecar CPU 问题已修复：W 观察到 `accompaniment-sidecar.service` 的 `python start.py` 闲时约 46.9% CPU，根因是 sidecar `start.py` 使用 uvicorn `reload=True` 开发模式；W 已将 systemd 启动方式改为生产模式 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info`，`/docs` 返回 200，backend `/api/health` 返回 real，W 用 `top` 确认 CPU 已恢复正常。
- 历史失败：远程服务器首次 deploy 曾因缺少 `httpx` 和 `deploy.sh` strict mode trap 问题失败，已在后续版本修复。
- 历史失败：real 模式初次失败是因为 sidecar 未启动；后续发现 `/api/download` 对短链返回 JSON `code=400`，已在 `v0.1.4` 改为先解析 aweme_id 再用完整 `www.douyin.com/video/{aweme_id}` 下载。
- 重新发布时不应继续复用已失败尝试过的 `v0.1.0` 包名；下一次发布应使用新版本号或唯一标识。
- 远程服务器的入口脚本 `/opt/accompaniment-app/deploy.sh` 与发布包内的 `06_delivery/deploy.sh` 不是同一个文件；若本机 deploy 脚本有修复，发布步骤必须包含同步远程入口脚本。
- 技术方向是 Web/PWA + Python FastAPI + ffmpeg + Debian VM。
- 公开入口 `https://us.wumpus.top/` 已可通过 HTTPS 访问父辈界面。
- admin 入口 `https://us.wumpus.top/admin/` 已可通过 HTTPS 访问，并返回 Basic Auth 鉴权挑战。
- 本地前端已改善手机粘贴体验：父辈界面新增“粘贴链接”按钮，支持浏览器剪贴板读取；不支持或失败时提示长按输入框选择粘贴。Playwright 手机视口 mock 流程验证已通过，截图为 `/private/tmp/accompaniment-mobile-paste.png`；该改动尚未发布到线上。
- 本地前端已为任务恢复/结果页面增加“重新开始”按钮：点击后清除 `?task=`、清空输入框、清除本地任务记录并回到主页初始状态。Playwright 手机视口验证已通过，截图为 `/private/tmp/accompaniment-home-button.png`；该改动尚未发布到线上。
- 本地前端已调整成功页布局：右上角显示“返回首页”，版本号移到页尾；成功页分为播放器、当前播放/下载、变调区域；半音选择显示“1 = 半音，2 = 全音”；当前音频链接有效期按当前播放/下载版本的 `created_at + 7天` 显示为绝对日期。Playwright 手机视口验证已通过，截图为 `/private/tmp/accompaniment-result-layout.png` 和 `/private/tmp/accompaniment-return-home.png`；该改动尚未发布到线上。
- 本地前端已接入上传入口：主页增加“上传手机里的音频”，支持选择 `mp3/m4a/wav`，上传成功后直接进入现有结果页、播放器、下载和变调流程；Playwright 手机视口上传冒烟通过，截图为 `/private/tmp/accompaniment-upload-entry.png`；该改动尚未发布到线上。
- 本地目录已初始化为 git 仓库，并关联远程 `origin`：`https://github.com/Min10873/Accompaniment-mobile-app.git`；尚未提交或推送。
- 女儿需求通过 learning trace 实现，记录人和 agent 如何协作。
- 生产反馈和手机 UX 迭代已记录 learning trace：`07_traces/sessions/2026-05-17-production-feedback-and-mobile-ux.md`。
- 多 agent 无状态任务包模式已记录 decision trace：`07_traces/decisions/worker-task-packet-model.md`。
- 音频上传和两页式父辈页逻辑已形成产品草案：`03_product/product_design_v2.md`。
- UI 风格正在等待 Gemini 网站输出视觉探索稿；M 后续负责审查可用性并整合到现有前端。
- Q 已回收 Gemini UI 可用性审查：Gemini 黑金控制台方向有高级感，但不能直接采用；后续 UI 实施必须避免过度设计、暗色低对比、小字、英文术语、夸大宣传、自定义复杂播放器和过密半音按钮。
- P 已回收 Gemini UI 产品评审：采用黑金/控制台/舞台感、卡片分区、教程弹窗、半音说明；拒绝英文标签、复杂自定义播放器、跳动 VU/旋转黑胶等干扰项。
- UI 文案决策已定：不用“发烧级/Hi-Res/无损/AI算法/指定助手”，改用“智能伴奏台/专业伴奏控制台/专属音乐工作室/高品质伴奏提取/智能音频处理”等稳妥表达。
- 变调 UI 决策已定：后端可保留 `1-11`，父辈 UI 默认只展示 `1-5` 半音，暂不做 `6-11` 高级入口。
- I 已返回上传后端最小实现方案，并已保存为 `02_vibe/results/I-UPLOAD-BACKEND-PLAN-01.result.md`。
- 上传后端决策建议已定：首版保留原格式不转码，上传成功直接返回 `201 Created + status=done`，使用随机文件名，不保留用户原文件名，上传来源用 `source="upload"` 标记。
- 上传后端实现任务包已生成：`02_vibe/tasks/I-UPLOAD-BACKEND-IMPLEMENT-01.md`，结果路径为 `02_vibe/results/I-UPLOAD-BACKEND-IMPLEMENT-01.result.md`。
- I 已返回上传后端实现，M 已本地复核并补齐部署依赖：`POST /api/uploads` 支持 `mp3/m4a/wav`、20MB 限制、随机文件名、上传成功直接创建 `done` 任务，并返回 `audio_url`、`audio_variants.original` 和 `expires_at`；M 补充 `app/backend/requirements.txt` 中的 `python-multipart`，并放宽 `application/octet-stream` 上传兜底以兼容手机/通用表单上传；重新运行 `python3 -m pytest app/backend/tests -q`，结果 `45 passed`。
- 上传前后端联调验证任务已派出：`02_vibe/tasks/Q-UPLOAD-FRONTEND-VALIDATE-01.md`，建议使用 `gemini flash`，结果路径为 `02_vibe/results/Q-UPLOAD-FRONTEND-VALIDATE-01.result.md`。
- Q 已返回上传前后端联调验证，结论为通过：有效上传、错误上传、首页入口、结果页播放器/下载/复制/变调/绝对有效期、抖音粘贴入口和返回首页回归均通过；剩余风险是未在真实物理手机上测试，剪贴板权限仍需真实手机观察。
- 新目录已成为当前主线：`00_inbox/` 到 `07_traces/`。
- 旧问题和旧输出已复制到 `99_archive/`。

## 当前未做

- 手机粘贴体验、返回首页和成功页布局改动尚未发布和真实手机实测。
- 音频上传后端和前端入口已在本地实现，并通过 M 冒烟验证和 Q 联调验证；线上尚未发布，真实手机尚未测试。
- UI 视觉风格尚未定稿，等待 Gemini 方案回收。
- 未把当前可用版本提交并推送到 GitHub。
- 未删除旧目录。
- 旧目录仍保留：`thinks/`、`context/`、`agents/`、`workflows/`、`memory/`、`specs/`、`environment/`、`outputs/`、`traces/`。

## 下一步候选

1. 发布并手机实测粘贴体验、返回首页、成功页布局和上传入口改动。
2. 明确 `deploy.sh rollback` 在 systemd 管理后的使用边界，避免误用 legacy pid 启停。
3. 旧目录仍可稍后清理；删除前必须再次确认。

## 待清理旧目录

删除前必须确认：

```text
thinks/
context/
agents/
workflows/
memory/
specs/
environment/
outputs/
traces/
```
