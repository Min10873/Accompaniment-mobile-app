# Session Trace: MVP V1 Boundary and Acceptance Freeze

## 目标

回收 P 和 Q 的 worker 结果，把 MVP V1 的产品边界和验收方向整理成 W 可确认的项目事实，并保留下一步进入工程创建前必须冻结的技术点。

## 人的输入

W 先让 M 给建议。M 建议先让 P 复核 MVP V1 边界，再让 Q 把边界转成验收清单，最后再进入 I 的工程创建和实现任务。

P 返回 `P-R` 后，M 整合出 6 条需要 W 确认的决策。W 明确回复“6条决策同意”。

随后 W 粘贴了 `Q-R`。Q 把 P 的产品边界转成了手机网页、API、真实链路、交付风险和失败模式验收清单，并指出 I 创建工程前还需要冻结 API 契约、任务状态、错误码、UI 映射、7 天保留策略、并发限制和测试1真实链路输入。

## M 的理解

M 将 P/Q 输出视为建议和验收分析，不直接当成项目事实。W 确认的 6 条决策成为项目事实：

1. MVP V1 只做“抖音分享文本 -> MP3 音频链接”。
2. V1 不做变调、不做搜索、不做账号、不做历史列表、不做原生 App。
3. 成功页优先显示音频播放器，复制链接作为次操作。
4. 失败页只给老人看人话错误，技术细节只留后台记录。
5. V1 后端任务状态采用 `queued`、`downloading`、`extracting`、`done`、`failed`、`expired`，前端可合并展示。
6. V1 暂不使用数据库，用 JSON 任务记录和文件存储支撑 7 天保留。

## 任务拆解

| 子任务 | Owner | 输出 | 完成标准 |
|---|---|---|---|
| MVP V1 边界复核 | P | `P-R` | 明确必须做、后做、不做、页面状态和后续任务 |
| MVP V1 验收计划 | Q | `Q-R` | 覆盖 UI、API、真实链路、失败模式和交付风险 |
| 结果整合 | M | 决策清单和下一步建议 | 只把 W 确认内容作为项目事实 |
| 决策确认 | W | “6条决策同意” | 冻结第一批 MVP V1 事实 |

## 执行过程

| 步骤 | 动作 | 产物 |
|---|---|---|
| 1 | M 建议先 P、再 Q、最后 I | 避免直接写代码导致边界返工 |
| 2 | P 返回产品和架构边界建议 | MVP V1 极窄闭环、状态建议、I/Q 任务拆分 |
| 3 | M 整合 P 输出并提出 6 条待确认决策 | W 可逐条确认的冻结点 |
| 4 | W 确认 6 条决策 | 这些内容成为项目事实 |
| 5 | Q 返回验收计划 | UI、API、真实链路、失败模式和交付风险清单 |
| 6 | M 记录本次 raw learning trace | 保留人和 agent 如何协作冻结 MVP 的过程 |
| 7 | W 确认 Q 提出的工程前冻结点 | 并发无等待队列、测试1为首个 E2E 样本、公开不可猜链接、过期/不存在语义、复制按钮 |
| 8 | M 固化产品、架构、测试策略和 current state | `03_product/mvp_v1.md`、`04_architecture/system_design.md`、`05_testing/test_strategy.md`、`01_context/current_state.md` |
| 9 | I 返回 API 契约冻结建议 | POST/GET 契约、任务 JSON schema、错误码、contract tests |
| 10 | I 返回后端骨架实施计划 | 建议先创建可测试 FastAPI 契约骨架，mock worker，后续再接真实 sidecar 和 ffmpeg |
| 11 | I 回收并审查已创建的 app/backend/ 骨架 | 发现 `POST /api/tasks` 响应与落盘状态不一致，需要修正 |
| 12 | Q 生产环境摸底结果回收 | Debian 12 VM 可承载 V1 小闭环，但 Python 缺 pip，80/443 未开服务，x-ui/xray 已占用多个端口 |
| 13 | I 返回真实 sidecar / ffmpeg 代码接入结果 | 代码路径已接上，21 tests 通过，但尚未做 live sidecar / live ffmpeg 验证 |
| 14 | Q 更新部署设计和 runbook | 去掉 80/443 理想化入口，写实 VM 资源、swap、pip/venv、目录和回环端口策略 |
| 15 | W 再次纠正 M 的角色边界 | 本机 live API 验证也应派给 I，不应由 M 直接执行 |
| 16 | oldI 返回本机 live API 契约验证结果 | FastAPI HTTP API 契约通过，真实 sidecar / ffmpeg 仍未验证 |
| 17 | W 开启关键词搜索抖音预研支线 | 该支线交给 I-Pre，定位为 V1.1/backlog 预研，不改变当前 V1 主线 |
| 18 | I-Pre 返回关键词搜索预研结果 | 技术可 POC，但不建议进 V1；“第一个结果”有高产品风险，建议 P 复核 |
| 19 | oldI 返回本机真实链路 live 验证结果 | 测试1分享文本到 MP3 的本机真实链路通过，VM 仍待验证 |
| 20 | I 返回最小上线包和 deploy.sh | 生成 `dist/accompaniment-app-v0.1.0.tar.gz`，通用脚本支持 deploy/start/stop/restart/status/rollback |
| 21 | W 在 VM 上执行首次 deploy | 依赖安装成功但 pytest 失败，缺 `httpx`；deploy 脚本又报 `staging: unbound variable` |

## 关键决策

| 决策 | 原因 | 影响 |
|---|---|---|
| V1 只做抖音分享文本到 MP3 链接 | 父母当前真实流程是从抖音/视频提取伴奏音频 | 工程可以围绕单链路设计 |
| 不做变调、搜索、账号、历史、App | 这些都会扩大产品、UI 和后端复杂度 | V1 聚焦可用闭环 |
| 成功页播放器优先 | 老人目标是能播放伴奏，不是管理链接 | UI 不被技术链接抢主操作 |
| 失败页只显示人话错误 | 避免老人把技术失败理解成自己不会用 | 后台保留任务号和错误码供 W 排查 |
| 后端状态集合冻结为 6 个 | 前端可稳定映射状态，QA 可稳定验收 | 现有文档中若还有 `parsing/rejected`，后续需清理一致 |
| V1 不用数据库 | 单机、低并发、7 天保留用 JSON 足够 | 降低工程和部署复杂度 |

## 验证

本次没有运行代码或服务。验证方式是协议性验证：

- P 和 Q 的 worker 输出被 M 回收。
- M 没有把 worker 输出直接写成事实。
- W 明确确认 6 条决策。
- Q 的验收清单指出工程创建前还需冻结的剩余细节。

## 结果

已完成：

- MVP V1 第一批产品和架构边界已经由 W 确认。
- Q 的验收计划已经回收，成为下一轮 M 整合和 I 任务设计的输入。
- W 进一步确认：V1 并发策略先简化为“不等待”，只要当前有任务处理，新提交就直接返回 busy；音频链接使用公开但不可猜的随机链接；过期任务查询返回 `HTTP 200 + status: expired`，不存在任务返回 `404 TASK_NOT_FOUND`；首版成功页必须有“复制链接”按钮，但播放器仍是主操作。
- W 听完解释后确认：测试1分享文本作为 MVP V1 首个真实 E2E 验收样本。它不是限制产品只能支持一个视频，而是先用一个固定真实样本证明主链路成立。
- I 回收后新增待 W 确认点：`POST /api/tasks` 成功是否用 `201 Created`；任务记录是否只保存 `share_text_preview` 而不保存完整 `share_text`；已创建任务的业务失败是否仍用 HTTP 200，由 `status` 和 `error_code` 表示。
- W 确认上述 3 点都“可以”。M 将其固化为 API 契约事实。
- I 进一步建议第一阶段创建 `app/backend/` 最小 FastAPI 后端骨架，只实现 API 契约、链接提取、JSON 任务记录、无等待队列 busy 判断、mock worker 和静态音频文件挂载；第一阶段不接真实 sidecar，不运行真实 ffmpeg。
- I 审查后指出：当前骨架总体可保留，但 `POST /api/tasks` 需要先只落盘 `queued`，不能同步把记录推进到 `done`，否则轮询契约失真。
- Q 生产环境摸底显示：目标 VM 是 Debian 12，1 core，约 961Mi 内存，根盘约 18G 可用，另有 `/data` 约 19G 可用；ffmpeg/ffprobe 已安装；Python 3.11.2 已有但无 pip，venv 可用；nginx/apache/caddy 均 inactive；域名 `us.wumpus.top` 指向该机但 80/443 当前连接失败；x-ui/xray 正在运行并占用 `9999`、`2096`、`18845` 以及本机 `11111`、`62789`。
- W 人工在 VM 上补齐并验证 Python 环境：`python3 -m pip --version` 返回 pip 23.0.1；`python3 -m venv /opt/accompaniment-app/venv` 创建成功；`/opt/accompaniment-app/venv/bin/python -m pip --version` 返回 venv 内 pip 23.0.1。
- I 将后端从 mock 过渡到真实 sidecar / ffmpeg 代码路径，并通过边界测试锁住行为；但 live sidecar / live ffmpeg 还未跑，需要后续实测。
- Q 将 `04_architecture/deployment_design.md` 和 `06_delivery/runbook.md` 更新为真实 VM 边界：不动 VPN/x-ui/xray，FastAPI 和 sidecar 先走回环端口，代码/数据/日志分离，单任务忙时直接 `SERVER_BUSY`，不默认走 80/443。
- W 指出 M 又倾向于自己执行本机 live API 验证。M 纠正：即使是本机验证，只要属于 implementation 验证，也应生成 `I-TASK` 交给 I；M 的职责是主控、整合、决策建议和 trace，不应抢 I 的执行工作。
- oldI 完成本机 live API 验证：`pytest` 21 passed；本机 `8001` 被 Docker 占用，临时使用 `127.0.0.1:8011`；`GET /api/health`、正常 `POST /api/tasks`、查询 queued、无链接 422、忙碌 503、不存在任务 404 均符合契约；服务已停止，临时数据已清理。
- W 新开 I-Pre 预研“关键词搜索抖音并取第一个视频作为输入”。M 将其定位为 V1.1/backlog 技术预研，不写入 V1 事实，不改变当前分享文本输入主线。
- I-Pre 预研显示：关键词搜索技术上可以做 POC，但当前 sidecar 没有稳定公开的关键词搜索路由；商业 API 如 TikHub 有搜索能力但引入 API Key、费用、限流和依赖风险；“第一个视频”可能不是伴奏，需 P 复核是否应改为展示候选让人选择。
- oldI 完成本机真实链路 live 验证：sidecar 监听 `127.0.0.1:8000`，测试1分享文本经 `process_task_real()` 下载、ffmpeg 提取，任务 `5AXBVGGM` 最终 `done`，音频 `/files/audio/2lw46vth4umc.mp3` 大小约 7.7M，duration 约 11 分 45 秒，44.1kHz stereo，本机 HTTP HEAD 返回 200 和 `audio/mpeg`。
- I 完成最小上线包流程：新增 `06_delivery/package_release.sh` 和 `06_delivery/deploy.sh`，生成 `dist/accompaniment-app-v0.1.0.tar.gz`；包内只包含生产所需后端和部署脚本，不包含 `.poc`、`00_inbox`、`07_traces`、运行数据、`__pycache__` 或 `.pyc`。
- W 将包部署到 VM 时，pip 已成功安装 FastAPI、pytest、uvicorn 等依赖，但 pytest collection 阶段失败：`fastapi.testclient` 需要 `httpx`，`app/backend/app/downloader.py` 也直接 import `httpx`。随后 `/opt/accompaniment-app/deploy.sh` 报 `line 1: staging: unbound variable`。`deploy.sh status` 输出 `current=`、`backend=stopped`，说明首次 deploy 未完成。

未完成：

- 已把确认内容先写入 `03_product/mvp_v1.md` 和 `04_architecture/system_design.md`。
- 已把 Q 的验收清单写入 `05_testing/test_strategy.md`，包括 UI 状态、API 契约、真实链路和部署前预检。
- 已把 I 的 API 契约细节写入 `04_architecture/system_design.md` 和 `05_testing/test_strategy.md`。
- 尚未创建 `app/backend/` 正式工程骨架；这是创建代码工程的大动作，需 W 明确授权。
- 尚未创建正式代码工程。
- 尚未运行下载、ffmpeg、API 或 UI 测试。
- 尚未形成部署设计更新；需将生产环境摸底结果写入 `04_architecture/deployment_design.md` 或 `06_delivery/runbook.md`。
- 本机 live sidecar / live ffmpeg 验证已通过。
- Debian VM live sidecar / live ffmpeg 验证尚未执行。
- 尚未进入部署脚本或 systemd/nginx 细化阶段。
- 尚未在 VM 上执行 `deploy.sh deploy`。
- 已在 VM 上执行首次 `deploy.sh deploy`，但失败；下一步需要修正依赖和 deploy 脚本后重新打包部署。
- 本机 live API 验证已通过，但真实 sidecar 下载和真实 ffmpeg 提取仍未 live 验证。

## 给女儿看的解释

这一步展示了一个重要的软件工程方法：先冻结边界，再写代码。

P 的作用是帮助团队回答“我们到底做什么、不做什么”。Q 的作用是把这些边界变成可以检查的标准。M 的作用不是盲目接受 worker 的输出，而是把建议整理成决策问题，再交给人确认。

这里最关键的是 W 的确认。只有 W 说“6条决策同意”，这些内容才变成项目事实。这样做可以避免 agent 自己扩大范围，也能让后续实现和测试都围绕同一组明确目标展开。

后续过程中，M 两次差点直接承担 I 的实现或验证工作。W 及时指出：“你是 M，为什么不派出去？”这暴露了多 agent 协作里一个真实问题：主控 agent 为了推进效率，容易越过角色边界。

这对学习者很有价值。软件工程不只是把事情做完，还要让职责清楚。M 如果自己写代码、自己验证、自己验收，就会失去分工复核的意义。W 把 M 拉回主控角色，保留了 P/I/Q worker 的独立判断，也让每一步结果都能被回收、质疑和确认。
