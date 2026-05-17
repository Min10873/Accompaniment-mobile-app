# Worker Result: I-UPLOAD-BACKEND-PLAN-01

I-R:

结论：
- 最小方案是把“上传音频”做成和现有 `task -> audio_variants -> pitch` 同一条链路，只新增一个上传入口，落到同一份 `TaskRecord`。
- 建议 `POST /api/uploads`，成功后直接返回 `task_id`、`status=done`、`audio_url`、`audio_variants.original`，这样前端可以无缝进入现有结果页。
- `expires_at` 应该由后端直接返回，至少要返回在 `TaskRecord` 和每个 `AudioVariant` 上；前端不应只靠 `created_at + 7天` 推算。

实现/技术结果：
- 提议接口：
  - `POST /api/uploads`，`multipart/form-data`
  - 字段：`file`
  - 返回：沿用 `TaskResponse`
- 处理逻辑：
  - 先校验文件存在、单文件、扩展名/`Content-Type`、大小 <= 20MB。
  - 创建 `TaskRecord`，状态可直接置为 `done`，因为上传不需要下载/抽音频处理。
  - 生成一个不可猜的音频文件名，保存到 `AUDIO_DIR`，扩展名保留原始类型或统一转成 `.mp3` 取决于是否做转码。
  - 同步创建 `audio_variants["original"]`，作为当前播放/下载的原音频版本。
- 存储和文件名策略：
  - 文件名建议仍用随机 token，不用用户原文件名。
  - 目录仍沿用 `data/audio/` 和 `data/tasks/`。
  - 上传文件如果不转码，建议按原始后缀保存，另外在 `AudioVariant` 里记录 `kind="original"`、`source="upload"`。
  - 如果后续希望统一播放兼容性，再加一层转码到 mp3，但这不是最小实现。
- `TaskRecord` / `AudioVariant`：
  - `TaskRecord` 直接复用现有结构，新增一条上传来源的任务。
  - `audio_variants.original` 需要包含 `created_at`、`audio_url`、`audio_path`、`label="原调"`。
  - 任务完成后 `audio_url` 仍指向当前版本，结果页无需改大逻辑。
- 20MB / 文件类型验证：
  - 服务端必须做实际字节大小校验，不能只信前端。
  - 建议白名单：`mp3`、`m4a`、`wav`。
  - 再做一次 MIME/魔数校验，至少防止明显的伪装文件。
- 测试建议：
  - `POST /api/uploads` 正常上传返回 `201` 或 `200`，并创建 `done` 任务。
  - 超过 20MB 返回 `413` 或 `422`，且不落盘。
  - 非白名单类型返回 `422`。
  - 空文件/缺文件返回 `422`。
  - 上传后 `GET /api/tasks/{task_id}` 能返回 `audio_url` 和 `audio_variants.original`.
  - 上传后 `/files/audio/...` 可访问。
  - 上传任务进入现有 pitch 流程，能创建变调任务并命中缓存逻辑。
  - 返回体中应包含 `expires_at`，并验证它和任务保留期一致。
- 需要改的文件：
  - `app/backend/app/main.py`
  - `app/backend/app/models.py`
  - `app/backend/app/task_store.py`
  - `app/backend/app/worker.py`
  - `app/backend/tests/test_api_contract.py`
  - 可能还要补 `app/backend/app/config.py`，如果上传限制和保留期配置当前不在那边。

需要 W 决策：
- 上传文件是否保留原格式，还是统一转成 mp3。
- 上传成功后是直接返回 `done`，还是也走一个短暂 `queued -> done` 的任务状态。
- `POST /api/uploads` 的返回码是否统一用 `201`。

需要 M 整合：
- 这条方案可以直接作为实现起点，且改动面足够小，适合先做后端契约和测试，再补前端入口。

Learning Trace 候选：
- 上传能力最小实现应复用现有 `TaskRecord + audio_variants + pitch` 结构，不另起一套上传结果模型。

本 session 未执行：
- 未修改任何文件
- 未运行测试
- 未启动服务
