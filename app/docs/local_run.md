# Local Run

## 当前能力

第一批代码只包含：

- 抖音短链接提取。
- FastAPI 健康检查。
- `POST /api/tasks` 假任务创建。
- 手机网页表单。

暂不包含：

- 真实下载。
- ffmpeg。
- 部署。

## 后端

待 W 确认安装依赖后运行：

```text
cd app/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 测试

待 W 确认安装依赖后运行：

```text
cd app/backend
pytest
```

## 前端

当前前端是静态文件：

```text
app/frontend/index.html
```

实际联调时需要由后端或静态服务托管。

