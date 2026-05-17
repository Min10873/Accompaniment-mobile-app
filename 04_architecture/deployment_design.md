# Deployment Design V1

## 目标

把 MVP V1 部署到 W 的 Debian VM，但部署动作由人执行，agent 只提供说明和脚本。

## 服务器条件

已知：

- 系统：Debian 12。
- 资源：1 core、约 961MiB memory、20G root disk，另有 `/data` 约 19G 可用。
- 域名：`us.wumpus.top`。
- 当前运行 VPN/3x-ui/xray。
- 80/443 当前不可直接用。
- `ffmpeg` / `ffprobe` 已安装。
- `python3 3.11.2` 可用，`pip` 已补齐，`venv` 可用。
- 已加 1G swapfile。

## 真实部署边界

V1 不是理想环境部署，必须按现网约束设计：

- 不动现有 VPN/3x-ui/xray。
- 不默认占用 80/443。
- 后端只监听本机回环地址。
- sidecar 只监听本机回环地址。
- 生产入口先走本机回环端口，公网入口后置。
- 单任务处理，忙时直接返回 `SERVER_BUSY`，不设置等待队列。
- 数据、日志、代码必须分离。
- 临时视频文件必须尽快删除，不能长期保留。

## 部署原则

- Agent 不直接登录服务器。
- Agent 不直接安装依赖。
- Agent 不直接启动或停止服务。
- Agent 可以提供采集信息脚本和安装脚本。
- W 在服务器上人工执行。
- 所有脚本执行前必须可读、可审查。

## 推荐服务结构

```text
Nginx/Caddy (later, if approved)
  -> static Web page
  -> FastAPI backend (loopback only)
  -> /files/audio/ static audio
```

## 端口建议

| 服务 | 建议 |
|---|---|
| FastAPI | `127.0.0.1:8001` 起步 |
| sidecar | `127.0.0.1:8002` 起步 |
| 静态音频 | 由后续反向代理暴露 `/files/audio/` |
| 公网入口 | 后置，不直接假定使用 80/443 |

实际端口需以 W 服务器现状为准，且不得与 x-ui/xray 冲突。

## 文件存储

建议目录：

```text
/opt/accompaniment-app/
  app/
/opt/accompaniment-app/venv/
/data/accompaniment-app/
  videos/
  audio/
  tasks/
  logs/
```

规则：

- 音频文件保留 7 天。
- 文件名使用随机 ID。
- 原视频可处理完成后删除，减少磁盘占用。
- 任务记录保留，用于排错和 learning trace。

## 资源约束

VM 较小，V1 必须限制：

- 1 core 下不做多线程并发处理。
- 进程内只保留 1 个后台 worker。
- 不设等待队列，已有任务处理中时新请求直接 `SERVER_BUSY`。
- 单个视频大小要受控。
- 文件保留时间固定 7 天。
- 日志大小要受控。

不做多 worker、多进程抢占式并发。

## 安全边界

V1 暂不做账号系统。

最低要求：

- 音频链接不可预测。
- 不暴露服务器目录列表。
- 不允许用户传任意 shell 参数。
- 后端只接受分享文本，不接受任意命令。

## 部署前检查

部署前由 W 执行信息采集：

```text
系统版本
磁盘空间
内存
已监听端口
swap
ffmpeg 是否存在
python 是否存在
pip / venv 是否存在
反向代理是否存在
域名解析与 80/443 可达性
现有 x-ui/xray 端口占用
```

## Live 验证边界

本轮只做本机与 Debian VM 的真实验证，不做公网入口：

- sidecar 绑定 `127.0.0.1:8000`
- FastAPI 绑定 `127.0.0.1:8001`
- 不使用 80/443
- 不动现有 VPN/3x-ui/xray
- 数据与日志放 `/data/accompaniment-app/`
- 代码放 `/opt/accompaniment-app/`
- 当前代码若仍写死 package-local `data/`，可用符号链接或挂载把它指向 `/data/accompaniment-app/`
- 任一端口冲突时立刻停止，不改现有 VPN/xray 端口

## 部署阶段

1. 本地创建工程并验证。
2. 生成服务器信息采集脚本。
3. W 在 VM 执行采集脚本。
4. 根据采集结果生成安装脚本。
5. W 审查并执行安装脚本。
6. M 根据输出判断是否部署成功。

## 不做

- 不直接操作 VM。
- 不影响 VPN/3x-ui/xray。
- 不做复杂 CI/CD。
- 不做多用户权限系统。
