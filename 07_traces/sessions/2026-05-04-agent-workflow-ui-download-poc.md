# Session Trace: Agent Workflow, UI Design, and Download POC Direction

## 目标

把伴奏应用从产品边界推进到可协作执行的状态：

- 固化多 session agent 协作机制。
- 确认抖音测试1/测试2的 MVP 边界。
- 形成老人端手机 UI 方案。
- 确认下载能力先以 sidecar 方式做 POC。
- 将当前主线切换为下载链路优先验证。
- 回收本机下载 POC runbook，明确 Python 优先、Docker 备选。
- 确认 V1 前后端 API 契约。
- 回收 Q 的验收清单，并把 Playwright 手机截图验收纳入 UI 测试方法。
- 回收 P 的视觉规格，并确认 UI mock 的颜色、字号、布局和六状态文案基准。
- 回收 I 的静态 UI mock，并由 W 直接打开本地页面检查后确认可接受。
- 回收 Q 的并行测试准备矩阵，明确 UI mock 和 MP4 POC 的通过/失败标准。
- 生成 UI mock 手机截图，并整理一篇给女儿看的阶段教程草稿。
- 修正 trace 机制，确保女儿学习材料不会被遗忘。

## 人的输入

W 做了几个关键判断：

- worker 不是由 M fork 出来的 subagent，而是 W 手动启动的独立 session。
- worker session 是有状态的；新开 session 由 W 决定。
- worker 角色启动命令必须固定，能从文件里复制。
- worker 可以改文件，但必须由单次 TASK 明确授权。
- `P-BOOT` 和 `P-TASK` 不应重复，BOOT 管固定规则，TASK 只写本次差异。
- 测试1进入 MVP V1；测试2进入 backlog；老人端 V1 只保留粘贴分享文本单入口。
- UI 决策确认：成功页默认不显示长链接；失败页显示小号任务号；主按钮用蓝色；处理中不做取消按钮。
- 下载技术方向确认：`Douyin_TikTok_Download_API` 先作为 sidecar 做 POC，POC 通过前不定为最终方案，Cookie 不进入仓库或 trace。
- W 指出 M 对女儿 learning trace 的关注不够，建议每次默认记录，结项时再筛选呈现。
- W 授权 M 直接决定 API 契约细节，M 选择了提交任务加轮询、422 拒绝无链接、相对 `audio_url`、短随机 `task_id`。
- W 提出可以用浏览器模拟手机测试，M 判断 Playwright 截图更适合 W 评审 UI。
- W 担心视频下载技术过不去会让其他工作白做，M 和 I 将下载 POC 提升为当前最高优先级。
- W 确认 UI 名称暂用“伴奏提取”，不加入额外亲切称呼文案，接受 P 的视觉规格作为 mock 基准。
- I 输出本机下载 POC 执行清单，M 将其作为可审查 runbook 固化，但没有执行任何命令。
- I 并行完成 `.poc/ui-mock/index.html` 静态页面，W 打开六个状态后确认“可以”。
- Q 在两个 I session 并行时提前准备测试矩阵，M 回收时发现 Q 文档中 query 参数写成 `?state=...`，而实际 UI mock 使用 `?mock=...`，后续验收以实际实现 `?mock` 为准。
- W 希望 learning trace 带截图，让 W 和女儿看到同一份材料。M 用 Playwright 生成 iPhone SE 和 Android 360px 两组 UI mock 截图，并写入教程草稿。
- I 完成本机 MP4 下载 POC，W 人工播放确认正常。W 要求移除 POC 副本的 GitHub 关联，避免后续 pull 或 commit。
- M 使用已下载 MP4 执行 MP3 提取 POC，生成可解码的 MP3，确认本机下载加音频提取链路通过。
- I 在 POC 通过后提出最小正式后端工程计划：FastAPI、JSON 文件任务存储、串行队列、sidecar 内部调用、ffmpeg 提取、静态音频文件服务。
- W 决定先做架构设计，而不是立即创建正式后端工程。
- W 希望架构文档用图表表达，M 将总体结构、后端模块、数据流和任务状态补成 Mermaid 图。
- W 追问 1 CPU 怎么处理，M 把 V1 运行策略定为单 worker 串行队列，最多 1 个等待位，不做多线程并发。
- W 指出 M 在部署修复后仍默认让 W 执行本机打包，这与“W 只负责远程服务器”的实际分工不符。M 将分工补充固化为：远程服务器由 W 操作，本机工作区由 M/I/Q 按职责处理。
- W 进一步指出 M 重新打包时继续复用 `v0.1.0`，且只要求上传 tar.gz，没有明确远程入口脚本 `/opt/accompaniment-app/deploy.sh` 与包内 `06_delivery/deploy.sh` 的区别。M 承认这是发布流程检查点缺失，并把发布步骤约定固化到 session protocol。
- W 在远程服务器上连续部署 `v0.1.1` 到 `v0.1.4`，逐步暴露并修复了依赖缺失、后台任务未触发、mock/real 模式不可控、sidecar 未启动、sidecar 端口配置错误、短链下载返回 JSON 业务错误等问题。
- W 最终确认 `v0.1.4` 在 real 模式下能完成真实闭环：提交抖音短链后任务从 `queued` 到 `done`，返回 MP3 链接，下载的 MP3 文件约 209 KB 且可以播放。
- Q 将“后端核心真实闭环通过一次”和“可交给父母使用”拆成两个验收门槛。M 和 W 接受该拆分，下一阶段先处理 sidecar 运维稳定性。
- W 将 sidecar 从临时 `nohup` 进程切换到 `systemd` unit：`accompaniment-sidecar.service` 运行中、绑定 `127.0.0.1:8000`、启用开机自启，并通过 `/docs` 和 `get_aweme_id` 轻量验证。
- 第一次 reboot 验收显示 x-ui/VPN 和 sidecar 能自动恢复，但主 FastAPI 后端不会自动启动。W 手动执行 `deploy.sh start` 后恢复，M 判断需要把 backend 也纳入 systemd。
- W 创建 `accompaniment-backend.service`，将主 FastAPI 后端切到 systemd 管理，并启用开机自启。第二次 reboot 后，x-ui/VPN、sidecar、backend 均自动恢复，`/api/health` 返回 real 模式。

## M 的理解

M 修正了自己的工作方式：

- 不能把“派活”理解为自动 fork subagent；本项目里的派活是给 W 可复制的 `P/I/Q-TASK`。
- `M/P/I/Q` 是多 session 协作角色，不是一次性问答。
- worker 输出不是项目事实；必须经 M 整合、W 确认后才固化。
- learning trace 不能靠临时想起，应成为默认工作流。

## 任务拆解

| 子任务 | Owner | 输出 | 完成标准 |
|---|---|---|---|
| 设计多 session 协作机制 | M + W | `02_vibe/session_roles.md` | 有固定 BOOT、TASK、RESULT 格式 |
| 产品边界复核 | P | `P-R` | 测试1/测试2边界清楚 |
| UI 效果稿 | P | `P-R` | 覆盖输入、处理中、成功、失败状态 |
| 下载技术预研 | I | `I-R` | 明确 sidecar POC 方向和风险 |
| 下载 POC 计划 | I | `I-R` | 明确先本机 POC、再 VM POC、通过标准 |
| API 契约设计 | I | `I-R` | 明确提交/查询接口、状态、错误码 |
| 验收清单设计 | Q | `Q-R` | 明确 API/UI/失败/交付验收标准 |
| UI 视觉规格 | P | `P-R` | 明确颜色、字号、布局、六状态文案 |
| 本机下载 POC runbook | I | `I-R` | 明确目录、预检、Cookie 边界、sidecar、下载、ffmpeg、清理 |
| 静态 UI mock | I | `.poc/ui-mock/index.html` | 六状态可本地打开，W 肉眼确认 |
| 并行测试准备 | Q | `Q-R` | UI mock 和 MP4 POC 验收矩阵 |
| 阶段教程草稿 | M | `07_traces/tutorials/02-agent-collaboration-and-ui-mock.md` | 用文字和截图解释本阶段协作 |
| 本机 MP4 POC | I + W | `.poc/douyin-download/work/test1.mp4` | MP4 下载成功，W 播放确认 |
| 本机 MP3 提取 POC | M | `.poc/douyin-download/work/test1.mp3` | MP3 生成成功，ffmpeg 可完整解码 |
| 最小后端工程计划 | I | `I-R` | 建议三段式实现正式后端 |
| 后端架构设计固化 | M | `04_architecture/system_design.md` | 正式后端目录、模块、存储、队列和 sidecar 边界 |
| 架构图表化 | M | `04_architecture/system_design.md` | Mermaid 总体结构图、模块图、时序图、状态图 |
| 1 CPU 运行策略 | M | `04_architecture/system_design.md` / `04_architecture/deployment_design.md` | 单 worker 串行队列，最多 1 个等待位 |
| 固化确认结果 | M | 产品/架构文档更新 | 只写 W 已确认内容 |
| 修正 trace 机制 | M + W | trace 协议更新 | 默认记录原始 trace |

## 执行过程

| 步骤 | 动作 | 产物 |
|---|---|---|
| 1 | W 纠正 M：不要 fork subagent，要生成可复制 prompt | 多 session 协作方向改变 |
| 2 | W 和 M 讨论角色短名、session 状态、BOOT/TASK/R 格式 | `M/P/I/Q`、`X-BOOT`、`X-TASK`、`X-R` |
| 3 | M 固化 session 角色规则 | `02_vibe/session_roles.md` |
| 4 | W 指出 TASK 与 BOOT 重复 | TASK 模板改为精简版 |
| 5 | P 返回产品边界分析 | 测试1进 MVP，测试2进 backlog |
| 6 | W 确认产品边界 | `03_product/mvp_v1.md`、`03_product/product_design_v1.md` 更新 |
| 7 | P 返回 UI 效果稿 | 老人端单页 UI 状态和文案 |
| 8 | W 确认 UI 决策 | `03_product/product_design_v1.md` 更新 |
| 9 | I 返回下载预研 | 推荐 sidecar POC，但不定最终方案 |
| 10 | W 确认技术方向 | `04_architecture/system_design.md`、`04_architecture/tech_stack.md` 更新 |
| 11 | W 提醒女儿 trace 不能被遗忘 | trace 机制改为默认记录 |
| 12 | I 返回 API 契约设计，W 让 M 决定细节 | `04_architecture/system_design.md` 更新 |
| 13 | Q 返回验收清单，M 整合剩余 API 错误行为和 Playwright 截图测试 | `04_architecture/system_design.md`、`05_testing/test_strategy.md` 更新 |
| 14 | I 返回下载 POC 计划，W 确认继续 | 下载链路优先级写入架构和 runbook |
| 15 | P 返回 UI 视觉规格，W 确认 | `03_product/product_design_v1.md`、`05_testing/test_strategy.md` 更新 |
| 16 | I 返回本机下载 POC runbook，M 固化为可审查步骤 | `06_delivery/runbook.md` 更新 |
| 17 | I 返回静态 UI mock，M 做基础检查，W 打开页面后确认可接受 | `.poc/ui-mock/index.html` 成为 UI mock 基准 |
| 18 | Q 返回测试准备矩阵，M 标出 `?state`/`?mock` 参数差异 | 后续 UI 验收以 `?mock` 为准 |
| 19 | M 生成 UI mock 截图并写教程草稿 | `07_traces/tutorials/02-agent-collaboration-and-ui-mock.md` 和截图资产 |
| 20 | I 完成本机 MP4 下载 POC，W 播放确认，M 移除 POC 副本 Git 元数据 | MP4 下载风险初步通过，音频提取仍待验证 |
| 21 | M 从已下载 MP4 提取 MP3 并做只读验证 | 本机下载加音频提取链路通过，HTTP 链接和部署仍待验证 |
| 22 | I 返回最小后端工程计划 | 下一步可进入正式工程创建，但必须经 W 明确授权 |
| 23 | W 要求先做架构设计，M 固化正式后端设计 | `04_architecture/system_design.md` 更新 |
| 24 | W 要求架构用图表表示，M 补 Mermaid 图 | 架构文档更适合 W 和女儿共同阅读 |
| 25 | W 询问 1 CPU 多线程策略，M 固化为单 worker 串行队列 | 运行约束更贴近 VM 资源 |
| 26 | W 纠正本机/远程服务器分工 | `01_context/current_state.md` 增加分工约定补充 |
| 27 | W 纠正发布包版本号和远程入口脚本问题 | `02_vibe/session_protocol.md` 增加发布步骤约定 |
| 28 | I 修复远程部署 blocker，M 重新打包，W 部署验证 | `v0.1.1` deploy 和 pytest 通过 |
| 29 | W 发现任务永久停在 `queued` | M 修复 FastAPI background task，`v0.1.2` 让任务推进到 `done` |
| 30 | W 验证 mock 音频 HTTP 下载成功 | M 明确 mock 和 real 边界 |
| 31 | M 将 mock/real 改为环境变量控制 | `v0.1.3` 可通过 `/api/health` 查看 `processing_mode` |
| 32 | W 切到 real 后发现 `DOWNLOAD_FAILED` | M/I 定位为 sidecar 未启动和依赖健康未验证 |
| 33 | W 按 runbook 部署 sidecar | sidecar 从错误的 `0.0.0.0:80` 改为 `127.0.0.1:8000` |
| 34 | W 发现 sidecar 短链 `/api/download` 返回 JSON `code=400`，但完整视频 URL 可下载 MP4 | M 修复 downloader：先解析 aweme_id，再用完整 URL 下载，并拒绝 JSON 错误 |
| 35 | W 部署 `v0.1.4` 并确认真实 MP3 可播放 | 远程服务器真实闭环第一轮通过 |
| 36 | Q 回收远程真实闭环验收 | 明确后端核心 loop accepted once，但未达到父母试用标准 |
| 37 | W 将 sidecar 切换为 systemd 管理 | `accompaniment-sidecar.service` active、enabled，轻量验证通过 |
| 38 | W 执行第一次 reboot 恢复验收 | x-ui/VPN 和 sidecar 自动恢复，backend 未自动恢复 |
| 39 | W 将 backend 切换为 systemd 管理 | `accompaniment-backend.service` active、enabled，绑定 `127.0.0.1:8001` |
| 40 | W 执行第二次 reboot 恢复验收 | x-ui/VPN、sidecar、backend 均自动恢复，health 保持 real |

## 关键决策

| 决策 | 原因 | 影响 |
|---|---|---|
| worker 由 W 手动启动 session | W 需要掌控上下文和复制结果 | M 只生成 BOOT/TASK，不自动 fork |
| P 不与 M 完全合并 | 轻量产品讨论由 M 做，正式边界可由 P 复核 | 保留复核能力，同时减少 session 负担 |
| BOOT 和 TASK 分层 | 避免重复和规则漂移 | BOOT 管固定规则，TASK 管本次差异 |
| 测试1进 MVP | 它验证指定抖音链接下载和提音频主链路 | 成为 V1 验收方向 |
| 测试2进 backlog | 搜索和选首位视频扩大产品范围 | V1 保持单入口 |
| UI 单页单任务 | 老人端应减少选择和误点 | 首页只粘贴分享文本并开始提取 |
| 下载方案先 sidecar POC | 候选项目匹配链路，但依赖 Cookie 和风控 | POC 通过前不作为最终方案 |
| 下载链路优先验证 | 如果下载过不去，MVP 主闭环无法成立 | UI/API 暂时冻结在设计和 mock/契约层 |
| POC 先本机再 VM | 先验证 Cookie、解析、下载、ffmpeg 主链路，再验证 VM 资源和部署风险 | 降低一次性上服务器排错复杂度 |
| POC 通过标准是可播放音频 | API 200 不代表真的拿到可用音频 | 必须验证 mp4、ffmpeg、播放性 |
| 本机 POC Python 优先，Docker 备选 | Python 更便于快速改私有配置、看日志、保存 mp4 和交给 ffmpeg | Docker 留到依赖冲突或 VM/部署阶段 |
| API 使用提交任务加轮询 | 下载和提取可能耗时几十秒，网页不应一直阻塞等待 | 前端用 `POST /api/tasks` 创建任务，再轮询状态 |
| 未识别链接返回 422 且不建任务 | 这是提交前输入错误，不需要产生任务记录 | UI 直接进入“没有找到抖音链接”状态 |
| `audio_url` 返回相对路径 | V1 部署域名仍可能变化，相对路径更简单 | 前端直接播放，复制完整链接后续再处理 |
| `task_id` 用短随机 ID | 方便 W 通过截图或微信排查 | 失败页可显示小号任务号 |
| `TASK_NOT_FOUND` 使用 404 | 任务不存在是资源不存在，但响应体仍需稳定错误码 | 前端能显示“没有找到这次任务” |
| 过期任务返回 `expired + TASK_EXPIRED` | 区分任务存在但音频过期 | 前端能提示重新提取 |
| UI 验收使用 Playwright 手机截图 | W 可以直接看图评审老人端体验 | 实现可先用 mock 状态截图，不必等真实下载 |
| UI 名称暂用“伴奏提取” | 清楚直接，老人能理解 | V1 不加入额外品牌化或亲切称呼 |
| 视觉规格作为 mock 基准 | 先稳定颜色、字号、布局和状态文案 | 后续 I 可按规格做截图页面 |
| 静态 UI mock 先通过 W 肉眼验收 | 在真实后端完成前先验证老人端页面是否看得懂 | 后续再做 Playwright 截图和真实流程验收 |
| 测试矩阵先于测试执行产生 | 两个 I 并行时先定义什么算通过，避免回收结果时只听口头成功 | UI 和 MP4 POC 都需要路径、状态、文件类型等客观证据 |
| 教程带截图 | W 和女儿可以看到同一份 UI 材料 | learning trace 从文字过程变成可共同评审的学习材料 |
| 本机 MP4 POC 通过 | 最高风险先拆成“能否下载可播放 MP4”验证 | 可以继续进入 MP3 提取或后端集成，但不能宣称完整音频 MVP 已通过 |
| 本机 MP3 提取 POC 通过 | 已有 MP4 后，ffmpeg 提取音频风险较低但仍需验证 | 可以进入后端 API、文件服务和 7 天保留设计实现 |
| 正式工程先做最小后端 | POC 已证明下载和提音频可行，但完整产品仍需 API、任务状态和文件服务 | 建议分三段实现，避免一次铺太大 |
| V1 任务存储先用 JSON 文件 | 用户少、目标是先打通闭环 | 后续多用户或高并发再换数据库 |
| V1 后台处理先串行 | VM 资源小，下载和 ffmpeg 都重 | 队列满时返回 `SERVER_BUSY` |
| 先固化架构再创建工程 | POC 通过后仍需明确正式工程边界 | 避免 `.poc` 候选代码污染正式工程 |
| 架构图表化 | 文字说明不够直观，图能展示模块关系和状态流转 | 后续实现和学习材料都更容易对齐 |
| 1 CPU 只做单 worker | 并发会把 CPU、磁盘、ffmpeg 压力放大 | 最多 1 个等待位，超出返回 `SERVER_BUSY` |
| POC 副本移除 Git 元数据 | 该目录只是本地验证材料，不需要继续 pull 或 commit | 降低误操作风险 |
| trace 默认记录 | 不应依赖 M 临时判断是否值得记录 | 阶段结项时再筛选成给女儿看的材料 |
| W 不默认负责本机工作区动作 | W 负责远程服务器，M/I/Q 应承担本机分析、修改、打包和验证 | 后续 M 不能把本机打包或检查默认推给 W |
| 每次发布使用新版本号或唯一标识 | 同名包会造成远程残留冲突，也让人难以确认新旧包 | 后续发布说明必须明确版本号和上传映射 |
| 区分包内脚本和远程入口脚本 | 远程执行的是 `/opt/accompaniment-app/deploy.sh`，不自动等于 tar 包内脚本 | deploy 脚本有修复时，发布步骤必须包含同步远程入口脚本 |
| mock/real 必须可观测 | 只知道任务 `done` 不足以判断是否真实下载 | `/api/health` 返回 `processing_mode`，远程 env 控制 real 模式 |
| 应用健康和依赖健康分开验证 | 主后端可运行不代表 sidecar 可用 | real 模式前必须检查 `127.0.0.1:8000`、sidecar docs、下载文件和 ffprobe |
| HTTP 200 不等于业务成功 | sidecar 可能用 HTTP 200 返回 JSON `code=400` | 后端下载器必须检查内容类型和 JSON 错误，不能只看 HTTP 状态和文件非空 |
| 短链和完整视频 URL 行为不同 | sidecar 能解析短链，但 `/api/download` 对短链失败，对完整 URL 成功 | 后端先解析 aweme_id，再构造完整 `www.douyin.com/video/{aweme_id}` |
| 远程真实闭环通过 | W 下载到的 MP3 可播放，证明 MVP V1 核心后端链路成立 | 下一阶段转向交付稳定性、sidecar 管理、前端入口和验收 |
| 后端闭环和父母可用分开验收 | 技术链路通过不等于老人端可使用 | 还需要进程管理、重启恢复、多样本回归、前端入口和公网访问 |
| sidecar 不混入 deploy.sh 管理 | sidecar 是第三方项目并依赖私有 Cookie，生命周期不同于主 FastAPI | 用独立 `systemd` unit 管理，`deploy.sh` 继续只管主后端 |
| backend runtime 也交给 systemd | reboot 证明 `deploy.sh start` 不会自动运行 | 主后端用 `accompaniment-backend.service` 管理，发布后用 systemd restart |
| deploy.sh 角色需要重新界定 | systemd 管 runtime 后，`deploy.sh` 的 pid 文件状态可能误导 | 暂定 `deploy.sh` 做 deploy/rollback，运行态用 systemctl |

## 验证

本次主要是文档和协作机制验证：

- W 确认后才固化产品和技术方向。
- P/I 输出被 M 整合后才进入项目文档。
- 未执行安装、启动服务、真实下载或服务器操作。
- Cookie 被明确排除在仓库和 trace 之外。
- 远程服务器真实链路最终由 W 手工执行并确认：`v0.1.4` real 模式下，抖音短链任务完成并产出可播放 MP3。
- sidecar 已由 W 手工切到 `systemd` 管理，并通过本机回环地址、docs、aweme_id 解析和主后端 real health 验证。
- 主 FastAPI 后端已由 W 手工切到 `systemd` 管理。第二次 reboot 验收确认 x-ui/VPN、sidecar、backend 都能自动恢复。

## 结果

已完成：

- 固化 `M/P/I/Q` 多 session 协作机制。
- 固化测试1/测试2的 MVP 边界。
- 固化老人端 V1 UI 状态和关键文案。
- 固化下载能力 sidecar POC 方向。
- 修正 trace 机制：默认记录原始过程，结项时筛选呈现。
- 完成远程服务器真实后端闭环第一轮验证：主后端、sidecar、ffmpeg、JSON 任务状态和 HTTP MP3 服务协同成功。
- 完成 sidecar 从临时 `nohup` 到独立 `systemd` 管理的第一轮切换和轻量验证。
- 完成主 FastAPI 后端从 `deploy.sh start` 手工运行到独立 `systemd` 管理的切换，并通过 reboot 恢复验收。

## 给女儿看的解释

这段过程展示了一个核心软件工程方法：先把协作协议设计清楚，再让多个 agent 分工。

W 没有直接让 agent 写代码，而是先要求 M 明确 worker 怎么启动、怎么接任务、怎么回传结果、谁能改文件、谁能做最终决定。这类似软件系统里的 API 契约：如果接口不清楚，后面的实现会混乱。

这段过程也展示了人的判断很重要。M 一开始误以为“派活”就是 fork subagent，W 纠正后，整个项目改成了由 W 控制多个独立 session 的模式。后来 W 又发现 TASK 和 BOOT 重复，推动 prompt 模板变得更稳定。

最后，W 再次纠正 M：不要忘记女儿学习 trace。于是 trace 从“有空再记录”变成了默认工作流。这说明项目目标不只是做出软件，也包括留下清晰的学习过程。
