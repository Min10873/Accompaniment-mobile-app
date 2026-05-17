# Runbook V1

## 目标

记录 W 如何部署、运行、验证和排错伴奏应用。

当前可用版本：

- 线上 `/api/health` 运行时报告：`v0.1.9`。
- W 已在手机和 admin 上测试当前版本，认为这是一个不错的可用版本。

当前已通过：

```text
公开 HTTPS 入口
-> 父辈界面提交抖音短链
-> FastAPI 创建任务
-> sidecar 下载 MP4
-> ffmpeg 提取 MP3
-> 返回 HTTP 音频链接和播放器
-> 支持下载和变调
-> W 已通过 admin 与父辈界面测试
```

当前待排查问题：

- 服务器闲时 Python CPU 已定位到 sidecar 主进程：`accompaniment-sidecar.service` 的 `start.py` 进程约 46.9% CPU；主 backend 约 0.1%。
- 初步根因：sidecar `start.py` 使用 uvicorn `reload=True`，这是开发模式热重载，不适合生产常驻。
- 已修复：sidecar systemd 启动方式已改为生产模式 `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info`；`/docs` 返回 200，backend health 返回 real，W 用 `top` 确认 CPU 正常。
- 手机端从抖音复制 URL 后回到父辈界面，不容易发现如何粘贴。

## 当前运行方式

远程服务器：

- Debian 12。
- 现有 VPN/x-ui/xray 不由本项目管理。
- 本项目不碰 80/443。
- 当前生产主后端只监听 `127.0.0.1:8001`。
- 当前生产 sidecar 只监听 `127.0.0.1:8000`。
- 新端口规范目标为：sidecar `127.0.0.1:7000`，主后端 `127.0.0.1:7001`；迁移前按当前生产事实操作，迁移后同步更新本 runbook。
- 公开父辈入口：`https://us.wumpus.top/`。
- 公开 admin 入口：`https://us.wumpus.top/admin/`，受 Basic Auth 保护。

systemd 服务：

| 服务 | 作用 | 端口 | 状态 |
|---|---|---|---|
| `accompaniment-backend.service` | 主 FastAPI 后端 | 当前 `127.0.0.1:8001`，目标 `127.0.0.1:7001` | enabled |
| `accompaniment-sidecar.service` | 抖音下载 sidecar | 当前 `127.0.0.1:8000`，目标 `127.0.0.1:7000` | enabled |
| `x-ui.service` | 现有 VPN/xray | 现有端口 | 不由本项目管理 |

重要边界：

- `deploy.sh` 暂时只作为 deploy/rollback 工具。
- 运行态由 `systemctl` 管理。
- 不再用 `deploy.sh start/stop/restart` 管理运行态。
- sidecar 的 Cookie 属于私有配置，不进入仓库、trace、对话或截图。

## 目录

主应用：

```text
/opt/accompaniment-app/
  current -> /opt/accompaniment-app/releases/vX.Y.Z
  releases/
  incoming/
  backups/
  venv/
  env
```

运行数据：

```text
/data/accompaniment-app/
  videos/
  audio/
  tasks/
  logs/
```

sidecar：

```text
/opt/accompaniment-sidecar/Douyin_TikTok_Download_API/
```

## 常用状态检查

```bash
systemctl status accompaniment-backend.service --no-pager
systemctl status accompaniment-sidecar.service --no-pager
systemctl status x-ui --no-pager
```

```bash
ss -ltnp | grep -E ':(8000|8001|9999|2096|18845)\b'
```

```bash
curl -sS http://127.0.0.1:8001/api/health
```

成功判断：

```json
{"status":"ok","processing_mode":"real"}
```

sidecar 轻量检查：

```bash
curl -sS -o /tmp/sidecar-docs.html -w 'sidecar_docs_http=%{http_code}\n' \
  http://127.0.0.1:8000/docs
```

```bash
curl -sS \
  'http://127.0.0.1:8000/api/douyin/web/get_aweme_id?url=https%3A%2F%2Fv.douyin.com%2FbMs3D8QlEQY%2F' \
  -o /tmp/sidecar-aweme.json

python3 -m json.tool /tmp/sidecar-aweme.json | head -n 20
```

成功判断：

- `/docs` 返回 `200`。
- `get_aweme_id` 返回 JSON 顶层 `"code": 200`。

## 发布新版本

本机生成包：

```bash
./06_delivery/package_release.sh vX.Y.Z
```

W 上传：

```text
本机 dist/accompaniment-app-vX.Y.Z.tar.gz
-> 远程 /opt/accompaniment-app/incoming/accompaniment-app-vX.Y.Z.tar.gz

本机 06_delivery/deploy.sh
-> 远程 /opt/accompaniment-app/deploy.sh
```

远程执行：

```bash
chmod +x /opt/accompaniment-app/deploy.sh
/opt/accompaniment-app/deploy.sh deploy /opt/accompaniment-app/incoming/accompaniment-app-vX.Y.Z.tar.gz
systemctl restart accompaniment-backend.service
```

发布后验证：

```bash
systemctl status accompaniment-backend.service --no-pager
curl -sS http://127.0.0.1:8001/api/health
```

注意：

- 发布后不要用 `/opt/accompaniment-app/deploy.sh start`。
- 发布后通过 `systemctl restart accompaniment-backend.service` 让 systemd 加载新的 `current` release。
- `deploy.sh status` 会显示 systemd 和旧 pid 两套信息；以 `systemd_backend` 为运行态事实。

## 启停

主后端：

```bash
systemctl status accompaniment-backend.service --no-pager
systemctl restart accompaniment-backend.service
systemctl stop accompaniment-backend.service
systemctl start accompaniment-backend.service
```

sidecar：

```bash
systemctl status accompaniment-sidecar.service --no-pager
systemctl restart accompaniment-sidecar.service
systemctl stop accompaniment-sidecar.service
systemctl start accompaniment-sidecar.service
```

开机自启检查：

```bash
systemctl is-enabled accompaniment-backend.service
systemctl is-enabled accompaniment-sidecar.service
```

预期：

```text
enabled
enabled
```

## 真实任务验证

提交任务：

```bash
curl -sS -X POST http://127.0.0.1:8001/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"share_text":"https://v.douyin.com/bMs3D8QlEQY/"}'
```

查询任务：

```bash
curl -sS http://127.0.0.1:8001/api/tasks/{task_id}
```

成功判断：

```json
{
  "status": "done",
  "audio_url": "/files/audio/xxxx.mp3"
}
```

下载 MP3：

```bash
wget http://127.0.0.1:8001/files/audio/{audio_file}
```

或：

```bash
curl -I http://127.0.0.1:8001/files/audio/{audio_file}
```

成功判断：

- HTTP 200。
- `content-type: audio/mpeg`。
- 文件大小明显大于 mock 音频。
- W 能播放。

## 重启恢复验收

重启：

```bash
reboot
```

重新 SSH 后检查：

```bash
uptime
systemctl status x-ui --no-pager
systemctl status accompaniment-sidecar.service --no-pager
systemctl status accompaniment-backend.service --no-pager
ss -ltnp | grep -E ':(8000|8001|9999|2096|18845)\b'
curl -sS http://127.0.0.1:8001/api/health
curl -sS -o /tmp/sidecar-docs.html -w 'sidecar_docs_http=%{http_code}\n' http://127.0.0.1:8000/docs
```

通过标准：

- x-ui active。
- sidecar active。
- backend active。
- `8000` 和 `8001` 都监听 `127.0.0.1`。
- health 返回 `processing_mode=real`。
- sidecar docs 返回 `200`。

## Cookie 更新边界

Cookie 只放在 sidecar 私有配置中：

```text
/opt/accompaniment-sidecar/Douyin_TikTok_Download_API/crawlers/douyin/web/config.yaml
```

规则：

- 不把 Cookie 写进本项目仓库。
- 不把 Cookie 写进 learning trace。
- 不把 Cookie 贴到对话。
- 不把包含 Cookie 的日志或截图发给 agent。
- 更新 Cookie 后重启 sidecar：

```bash
systemctl restart accompaniment-sidecar.service
```

更新后轻量检查：

```bash
curl -sS \
  'http://127.0.0.1:8000/api/douyin/web/get_aweme_id?url=https%3A%2F%2Fv.douyin.com%2FbMs3D8QlEQY%2F' \
  -o /tmp/sidecar-aweme.json

python3 -m json.tool /tmp/sidecar-aweme.json | head -n 20
```

## 常见问题

### backend health 失败

检查：

```bash
systemctl status accompaniment-backend.service --no-pager
journalctl -u accompaniment-backend.service -n 120 --no-pager
tail -n 120 /data/accompaniment-app/logs/backend.log
ss -ltnp | grep ':8001' || true
```

### sidecar 不可用

检查：

```bash
systemctl status accompaniment-sidecar.service --no-pager
journalctl -u accompaniment-sidecar.service -n 120 --no-pager
tail -n 120 /data/accompaniment-app/logs/sidecar.log
ss -ltnp | grep ':8000' || true
```

注意：

- 日志可能包含敏感信息，不要直接贴完整日志。
- 只贴脱敏后的错误码、路径和状态。

### 任务返回 `DOWNLOAD_FAILED`

先分层检查：

```bash
curl -sS http://127.0.0.1:8001/api/health
curl -sS -o /tmp/sidecar-docs.html -w 'sidecar_docs_http=%{http_code}\n' http://127.0.0.1:8000/docs
curl -sS \
  'http://127.0.0.1:8000/api/douyin/web/get_aweme_id?url=https%3A%2F%2Fv.douyin.com%2FbMs3D8QlEQY%2F' \
  -o /tmp/sidecar-aweme.json
python3 -m json.tool /tmp/sidecar-aweme.json | head -n 20
```

可能原因：

- sidecar 未运行。
- Cookie 失效。
- 抖音风控。
- 视频本身不可下载。
- sidecar 返回 JSON 业务错误。

### 任务一直 queued

当前版本不应长期停在 `queued`。

检查：

```bash
cat /data/accompaniment-app/tasks/{task_id}.json
tail -n 120 /data/accompaniment-app/logs/backend.log
```

如果 `downloading_at` 为空，说明后台任务没有触发或 backend 异常。

## rollback

回滚 release：

```bash
/opt/accompaniment-app/deploy.sh rollback
systemctl restart accompaniment-backend.service
curl -sS http://127.0.0.1:8001/api/health
```

如果 backend systemd 失败，需要临时回到旧方式：

```bash
systemctl stop accompaniment-backend.service
systemctl disable accompaniment-backend.service
ss -ltnp | grep ':8001' || echo "8001 is free"
/opt/accompaniment-app/deploy.sh start
```

如果 sidecar systemd 失败，需要临时回到 `nohup`：

```bash
systemctl stop accompaniment-sidecar.service
systemctl disable accompaniment-sidecar.service
ss -ltnp | grep ':8000' || echo "8000 is free"

cd /opt/accompaniment-sidecar/Douyin_TikTok_Download_API
nohup .venv/bin/python start.py > /data/accompaniment-app/logs/sidecar.log 2>&1 &
echo $! > /opt/accompaniment-sidecar/sidecar.pid
```

## 当前限制

- 还没有父母可直接使用的手机网页真实入口。
- 还没有公网域名/HTTPS 入口。
- 只确认一个真实抖音样本完成闭环。
- Cookie 仍是运维依赖。
- `deploy.sh status` 已只读显示 systemd runtime，但 `start/stop/restart` 仍是旧 pid 管理方式，运行态应继续使用 `systemctl`。
