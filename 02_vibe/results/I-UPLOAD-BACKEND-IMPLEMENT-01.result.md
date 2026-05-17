I-R:

结论：
- `POST /api/uploads` 已实现，成功上传直接创建 `done` 任务并返回 `201 Created`。
- 上传结果复用现有 `TaskRecord` / `TaskResponse` / `audio_variants.original`，可直接进入现有结果页和 pitch 流程。

实现/技术结果：
- 接口契约：`multipart/form-data`，字段名 `file`，支持 `mp3` / `m4a` / `wav`。
- 校验行为：
  - 缺文件：`422`，`UPLOAD_FILE_REQUIRED`
  - 空文件：`422`，`UPLOAD_FILE_EMPTY`
  - 不支持类型：`422`，`UPLOAD_FILE_TYPE_UNSUPPORTED`
  - 超过 20MB：`413`，`UPLOAD_FILE_TOO_LARGE`
  - 正常上传：`201`，返回 `status=done`、`audio_url`、`audio_variants.original`
- 上传文件使用随机文件名，保存在既有 `AUDIO_DIR`，不保留原始文件名，不做转码。
- `audio_variants["original"]` 的 `source` 设为 `"upload"`。
- `expires_at` 已返回在任务响应中，并同步写入 `AudioVariant.expires_at`。

修改文件：
- `app/backend/app/main.py`
- `app/backend/app/models.py`
- `app/backend/app/task_store.py`
- `app/backend/app/uploads.py`
- `app/backend/tests/test_api_contract.py`
- `app/backend/tests/test_task_store.py`

API 契约：
- `TaskResponse` 新增 `expires_at`。
- `AudioVariant` 新增 `expires_at`。
- 上传成功返回和普通 done 任务一致的结果结构，只是来源改为 upload。

验证结果：
- `python3 -m pytest app/backend/tests -q`
- 结果：`44 passed`

风险/阻塞：
- 当前只按扩展名和 `Content-Type` 做格式判断，没有做更深的音频魔数识别。
- V1 保留原格式，不转码，因此播放兼容性仍取决于客户端和浏览器对原文件的支持。

需要 W 决策：
- 暂无。

需要 M 整合：
- 前端如需展示上传入口，可直接消费现有任务详情返回的 `expires_at` 和 `audio_variants.original`。

Learning Trace 候选：
- 上传能力最小实现应复用现有任务模型和变调链路，不另起一套结果模型。

本 session 未执行：
- 未修改前端。
- 未启动长运行服务。
