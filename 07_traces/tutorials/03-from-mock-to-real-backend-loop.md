# Learning Trace: 从 mock 到真实后端闭环

## 这篇记录什么

这一阶段，我们把“看起来能跑”的后端推进到“真实下载并提取出可播放 MP3”。

最终通过的链路是：

```text
抖音短链
-> 主后端创建任务
-> sidecar 解析并下载 MP4
-> ffmpeg 提取 MP3
-> 主后端返回 HTTP 音频链接
-> W 下载 MP3 并确认可以播放
```

通过版本是 `v0.1.4`。

## 第一个学习点：部署成功不等于产品成功

远程服务器第一次部署失败，不是因为产品设计错了，而是因为交付细节没有准备完整：

- 后端代码 import 了 `httpx`，但 `requirements.txt` 没有声明。
- `deploy.sh` 使用 strict mode，退出时的 trap 引用了已经失效的 local 变量。
- 后来又发现远程入口脚本 `/opt/accompaniment-app/deploy.sh` 和包里的 `06_delivery/deploy.sh` 不是同一个文件。

W 指出一个关键问题：每次重新发布都不能复用旧包名，否则人无法判断上传的是旧包还是新包。

于是发布流程被固化：

- 每次发布使用新版本号。
- 明确列出要上传哪些文件。
- 明确远程执行的是哪个脚本。
- 明确包内脚本和远程入口脚本的区别。

这里的学习点是：

> 发布流程也是软件的一部分。版本号、脚本路径和上传清单都需要像代码一样精确。

## 第二个学习点：queued 不代表后台在工作

`v0.1.1` 部署后，API 可以创建任务：

```json
{"task_id":"1DMJPKQV","status":"queued"}
```

但任务一直停在 `queued`。

检查任务文件后发现：

```json
"downloading_at": null,
"extracting_at": null,
"done_at": null
```

这说明后端只写了任务记录，没有启动处理任务的 worker。

M 在 `v0.1.2` 中修复：

- `POST /api/tasks` 创建任务后，挂一个 FastAPI background task。
- 测试确认任务能从 `queued` 推进到 `done`。

这里的学习点是：

> 状态字段不是装饰。它们是观察系统是否真的在工作的证据。

## 第三个学习点：mock 和 real 必须可区分

一开始后端有 mock worker，可以生成一个假的 MP3。它适合测试 API 和文件服务。

但 mock 成功不等于真实下载成功。

所以 `v0.1.3` 增加了环境变量：

```text
ACCOMPANIMENT_MOCK_PROCESSING=false
```

并让健康检查返回运行模式：

```json
{"status":"ok","processing_mode":"real"}
```

这里的学习点是：

> mock 很有用，但必须清楚标记。否则人会把假闭环误认为真实闭环。

## 第四个学习点：health ok 不等于依赖 ok

主后端 health 正常：

```json
{"status":"ok","processing_mode":"real"}
```

但真实任务失败：

```json
{"status":"failed","error_code":"DOWNLOAD_FAILED"}
```

排查发现：主后端依赖的 sidecar 根本没有在 `127.0.0.1:8000` 监听。

也就是说：

```text
FastAPI 健康
不代表
sidecar 健康
```

后来 W 启动 sidecar，又发现它默认监听在 `0.0.0.0:80`，这不符合项目约定。修正顶层 `config.yaml` 后，sidecar 才监听：

```text
127.0.0.1:8000
```

这里的学习点是：

> 一个系统的健康检查要分层。主服务、依赖服务、真实业务链路都要分别验证。

## 第五个学习点：HTTP 200 不等于业务成功

sidecar 的 `/api/download` 有一个特别容易误导的行为：

```text
HTTP 200
```

但响应体可能是：

```json
{"code":400,"router":"/api/download"}
```

如果后端只检查 HTTP 状态和文件非空，就可能把 270 字节的 JSON 错误保存成 `.mp4`。

I 帮忙确认 sidecar 的下载 API 没变，真正的问题是：

```text
/api/download + v.douyin.com 短链 -> JSON code=400
/api/download + www.douyin.com/video/{aweme_id} -> MP4 成功
```

于是 `v0.1.4` 做了两个修复：

- 先调用 sidecar `get_aweme_id`。
- 再构造完整链接 `https://www.douyin.com/video/{aweme_id}` 去下载。
- 如果 sidecar 返回 JSON 错误，后端直接判定 `DOWNLOAD_FAILED`，不保存成 MP4。

这里的学习点是：

> 集成第三方服务时，不能只相信 HTTP 状态码。必须理解对方的业务错误格式。

## 第六个学习点：后端闭环通过不等于老人可用

W 最终确认：下载到的 MP3 可以播放。

这说明后端核心真实闭环通过了一次。

但 Q 进一步拆分了两个验收门槛：

```text
后端核心 loop accepted once
不等于
可交给父母使用
```

父母可用还需要：

- sidecar 能稳定随服务器启动。
- 手机网页入口。
- 公网域名和访问路径。
- 多个抖音样本回归。
- 失败时给老人看人话错误。

这里的学习点是：

> 技术闭环是里程碑，不是交付终点。真正交付要考虑使用者和运维。

## 第七个学习点：从 nohup 到 systemd

sidecar 最初用 `nohup` 临时启动。

这能让程序在 SSH 断开后继续跑，但不适合长期使用：

- 服务器重启后不会自动启动。
- 进程挂了不会自动拉起。
- 状态检查不统一。

所以 sidecar 被切到独立 systemd 服务：

```text
accompaniment-sidecar.service
```

验证结果：

- service 是 `active (running)`。
- 监听 `127.0.0.1:8000`。
- 已启用开机自启。
- `/docs` 返回 200。
- `get_aweme_id` 返回 `code=200`。

我们没有让 `deploy.sh` 管 sidecar，因为 sidecar 是第三方项目，并且依赖私有 Cookie。它和主 FastAPI 应用有不同生命周期。

这里的学习点是：

> 进程管理也是架构决策。不是所有服务都应该塞进同一个部署脚本。

## 人和 agent 各自做了什么

W 的关键作用：

- 操作远程服务器。
- 观察真实输出。
- 质疑 M 的错误假设。
- 确认 MP3 是否真的能播放。
- 提醒不要忘记给女儿记录学习过程。

M 的关键作用：

- 整合 P/I/Q 的结果。
- 判断下一步优先级。
- 修复本机代码和打包。
- 把结果固化到状态和 trace。

I 的关键作用：

- 修部署依赖和脚本 bug。
- 查 sidecar API。
- 产出 sidecar 运维 runbook。

Q 的关键作用：

- 区分“后端闭环通过”和“父母可用”。
- 列出剩余风险和下一步验收任务。

## 这一阶段的最终状态

已确认：

- `v0.1.4` 在远程服务器 real 模式下完成一次真实后端闭环。
- sidecar 已由 systemd 管理。
- MP3 文件可下载并播放。

尚未确认：

- 服务器重启后是否自动恢复完整链路。
- 多个抖音样本是否稳定。
- 手机网页是否能让父母顺利使用。
- 公网域名和 HTTPS 入口是否就绪。

## 给女儿的总结

这段过程展示了软件工程里一个很重要的思想：

> 不要把“某一层成功”误认为“整个系统成功”。

API 返回成功不够，任务状态要推进。

任务 done 不够，要知道是不是 mock。

health ok 不够，依赖服务也要健康。

HTTP 200 不够，内容必须是可用的视频。

MP3 生成不够，使用者还要能在手机上打开。

这就是为什么工程师需要把系统拆成层，一层一层验证，再把结果写成可复用的流程。
