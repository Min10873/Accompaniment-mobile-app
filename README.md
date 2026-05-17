# 伴奏应用开发

## 当前入口

后续优先读取新目录：

```text
00_inbox/
01_context/
02_vibe/
03_product/
04_architecture/
05_testing/
06_delivery/
07_traces/
99_archive/
```

旧目录暂时保留，只作历史参考。

## 新目录说明

| 目录 | 用途 |
|---|---|
| `00_inbox/` | W 的原始输入 |
| `01_context/` | 当前事实和状态 |
| `02_vibe/` | agent、session、task、memory、trace 协议 |
| `03_product/` | 产品范围和 MVP |
| `04_architecture/` | 技术栈、系统设计、部署设计 |
| `05_testing/` | 测试策略和验证清单 |
| `06_delivery/` | 运行、部署、排错说明 |
| `07_traces/` | 给女儿看的 learning trace |
| `99_archive/` | 旧问题、旧输出和历史材料 |

## 启动顺序

每次 session 开始，M 应先读取：

1. `01_context/current_state.md`
2. `01_context/user_answers.md`
3. `02_vibe/session_protocol.md`
4. 当前任务相关目录

## 当前硬规则

- 不经 W 确认，不做大动作。
- 大动作包括：创建代码工程、移动/删除文件、大规模重写文档、安装依赖、启动服务、操作服务器、一次修改超过 3 个文件。
- 文档迁移采用“复制后确认”，旧文件先不动。
- 服务器由 W 人工操作，agent 只提供可审查脚本或说明。

## 当前产品方向

MVP V1：

```text
手机网页输入抖音分享文本
-> 服务端下载视频
-> ffmpeg 提取音频
-> 返回 HTTP 音频链接
```

