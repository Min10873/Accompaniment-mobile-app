# Test Strategy V1

## 目标

验证 MVP V1 是否真正打通：

```text
抖音分享文本 -> 音频 HTTP 链接
```

## 测试原则

- 人不做测试，人只做验证。
- 测试由自动化脚本、agent 或工具执行。
- 测试报告必须说明为什么通过。
- 网页端测试优先考虑 Playwright。
- 测试报告最后应包含截图或截图路径。
- 可使用一部安卓旧手机作为应用端测试环境。

## 测试分层

| 层级 | 测什么 | 方式 |
|---|---|---|
| Unit | 链接提取、任务状态、文件命名 | 自动测试 |
| Integration | 下载工具、ffmpeg、文件输出 | 本地或 VM 验证 |
| UI | 手机页面输入、提交、结果展示 | Playwright 手机视口截图 + 浏览器检查 |
| E2E | 从分享文本到音频链接 | 手动验收优先 |

后续调整目标：

- UI 和 E2E 尽量由 Playwright 执行。
- W 只查看报告、截图和结论。

## Unit Tests

必须覆盖：

- 从完整抖音分享文本中提取 `https://v.douyin.com/.../`。
- 输入不含链接时返回明确错误。
- 多个链接时选择第一个抖音链接。
- 任务状态只能在合法状态中流转。
- 生成的音频文件名不可预测。
- 提交阶段无链接或服务忙时不创建任务记录。

## Integration Tests

必须覆盖：

- 下载工具可处理测试1真实抖音链接。
- 下载结果必须是非空 MP4，不能只看下载接口返回 200。
- ffmpeg/ffprobe 能识别视频和音频流。
- ffmpeg 可从视频中提取 mp3。
- MP3 必须非空、可解码、duration > 0。
- 输出文件可通过 HTTP 访问。
- 处理失败时任务状态变为 `failed`。
- 成功后临时 MP4 被清理，或有明确清理策略。

## UI Tests

必须覆盖：

- 手机视口下输入框可用。
- 提交按钮足够明显。
- 处理中状态清楚。
- 成功后音频链接可点击。
- 失败后错误信息能看懂。

### Playwright 手机截图验收

UI 实现后，优先用 Playwright 在手机视口生成截图，供 W 直接评审。

建议覆盖状态：

- `idle`：初始输入。
- `filled`：输入后可提交。
- `processing`：处理中。
- `success`：成功，显示播放器和复制按钮。
- `error`：通用失败，显示小号任务号。
- `no-link`：未识别抖音链接。
- `server-busy`：已有任务处理中，提示稍后再试。
- `expired`：任务或音频过期，提示重新提取。

建议覆盖视口：

- 常见 iPhone 竖屏宽度。
- 常见 Android 竖屏宽度。

截图检查重点：

- 字号和按钮是否适合老人。
- 主任务是否一屏可理解。
- 输入框、按钮、播放器、错误提示是否重叠。
- 长分享文本、长链接、任务号是否撑破布局。
- 成功页是否优先显示播放器。
- 失败页是否隐藏技术错误。
- 页面是否出现 V1 禁止项：搜索、变调、登录、历史列表、复杂导航。
- `success` 截图中播放器必须比复制按钮更靠上、更显眼。
- `error` 截图中任务号必须存在但视觉弱化。
- `no-link` 截图中不能出现“再试一次”，只引导重新粘贴。
- `server-busy` 截图不能显示技术错误，不能误导用户以为已经创建任务。
- `expired` 截图必须提示重新提取，不应继续展示不可播放链接。
- 复制失败状态如实现，需要单独截图确认完整链接不会横向撑破页面。

真实后端未完成时，可先用 mock 状态或 mock API 生成截图；不必等待抖音下载 POC 完成。

## API Contract Tests

必须覆盖：

- `POST /api/tasks` 正常输入返回 `task_id` 和 `queued`。
- `POST /api/tasks` 正常输入使用 `201 Created`。
- `POST /api/tasks` 无抖音链接返回 `422 NO_DOUYIN_URL`，不创建任务号，不创建任务记录。
- `POST /api/tasks` 已有任务处理中时返回 `503 SERVER_BUSY`，不创建任务号，不创建任务记录。
- 无链接或服务忙响应里的 `task_id` 和 `status` 都必须为 `null`。
- `GET /api/tasks/{task_id}` 只返回 V1 约定任务状态：`queued`、`downloading`、`extracting`、`done`、`failed`、`expired`。
- `GET /api/tasks/{task_id}` 已创建但处理失败的任务返回 `HTTP 200`、`status: failed` 和对应 `error_code`。
- `GET /api/tasks/{task_id}` 不存在任务返回 `404 TASK_NOT_FOUND`。
- `GET /api/tasks/{task_id}` 过期任务返回 `HTTP 200`、`status: expired` 和 `TASK_EXPIRED`。
- `GET /api/tasks/{task_id}` 成功时返回相对路径 `audio_url`。
- `/files/audio/{filename}` 可播放存在的音频文件；过期或不存在返回 `404`。
- `audio_url` 文件名必须随机不可猜，不暴露真实目录。
- 任务 JSON 只保存最多 80 字的 `share_text_preview`，不保存完整 `share_text`。
- API 响应和任务记录中不得保存或返回 Cookie、sidecar URL、服务器真实路径、ffmpeg 命令或完整 traceback。

## E2E 验收

使用测试1分享文本作为 MVP V1 首个真实 E2E 验收样本：

```text
抖音分享文本
-> 提取第一个抖音链接
-> 提交
-> 等待处理
-> 下载 MP4
-> ffmpeg 提取 MP3
-> 得到 HTTP 音频链接
-> 手机浏览器打开链接播放
```

通过标准：

- 链接能打开。
- 音频能播放。
- MP4 和 MP3 都不能只以 HTTP 200 作为通过依据，必须验证文件非空且可解码。
- 文件保留策略可解释。
- 失败时不让用户困惑。
- 老人端页面不得出现 Cookie、sidecar、ffmpeg、traceback、服务器路径或内部端口。

## Delivery Preflight

部署前由 W 人工执行或确认：

- Debian 12 系统版本。
- 磁盘和内存余量。
- 监听端口和现有 VPN/3x-ui 风险。
- Python 和 ffmpeg 可用。
- 反向代理路径和静态音频文件访问。
- `/files/audio/{filename}` 不暴露目录列表。
- 7 天清理策略可人工审查。

agent 只提供可审查说明或脚本，不直接操作服务器。

## 非目标

V1 不测试：

- 自动搜索抖音。
- 自动选伴奏。
- 变调。
- 账号权限。
- 大规模并发。
- 等待队列。

## 风险测试

需要额外关注：

- 抖音链接过期。
- 下载工具失效。
- VM 磁盘不足。
- ffmpeg 不存在或执行失败。
- 视频没有音轨。
- 处理时间过长。

## Trace 要求

每次关键测试应记录：

- 输入是什么。
- 期望是什么。
- 实际结果是什么。
- 问题如何定位。
- 最终如何修正。

这些记录进入 `07_traces/sessions/` 或 `07_traces/decisions/`。
