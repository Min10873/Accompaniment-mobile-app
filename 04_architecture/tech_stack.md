# Tech Stack V1

## 结论

MVP V1 采用：

```text
手机 Web/PWA
+ Python FastAPI 后端
+ Douyin_TikTok_Download_API sidecar POC
+ ffmpeg
+ Debian 12 VM
```

## 前端

形态：

- 手机优先 Web 页面。
- 可添加到手机桌面作为快捷方式。
- 暂不做原生 App。

实现：

- 先用简单 HTML/CSS/JS。
- 后续如复杂度上升，再考虑 React。

重点：

- 输入框大。
- 按钮大。
- 结果链接清楚。
- 适合老人操作。

## 后端

技术：

- Python FastAPI。

职责：

- 接收抖音分享文本。
- 提取抖音链接。
- 调用下载工具下载视频。
- 调用 ffmpeg 提取音频。
- 返回 HTTP 音频链接。
- 记录处理过程。

## 音视频处理

视频来源：

- V1 只做抖音。

下载：

- 优先以 `Douyin_TikTok_Download_API` 作为 sidecar 服务做真实 POC。
- POC 目标是验证指定抖音分享链接能下载为视频文件，再交给 `ffmpeg` 提取音频。
- POC 通过前，不把该项目定为最终方案。
- 该方案需要有效 Douyin Cookie；Cookie 不进入仓库、不进入 trace。
- `yt-dlp` 或其他下载工具保留为替代方案。

音频：

- 使用 `ffmpeg` 提取音频。
- V1 不做变调。
- V1.1 再评估 `ffmpeg + rubberband`。

## 部署目标

候选服务器：

- W 的美国 Debian 12 VM。

已知条件：

- 1 core。
- 1G memory。
- 20G disk。
- 域名：`us.wumpus.top`。
- 当前运行 VPN/3x-ui。
- 服务器由人操作，agent 不直接操作。

## 关键约束

- 不能影响现有 VPN/3x-ui。
- 文件保留 7 天。
- 需要限制并发和文件大小。
- 公开 HTTP 链接应使用随机文件名。
- 部署脚本可由 agent 提供，但由 W 执行。

## 风险

- 抖音下载稳定性。
- Douyin Cookie 失效、风控或地区访问导致下载失败。
- sidecar 服务增加运行组件，需要端口隔离、日志和重启策略。
- VM 资源较小。
- ffmpeg 依赖安装和磁盘占用。
- HTTP 文件链接的访问控制。
