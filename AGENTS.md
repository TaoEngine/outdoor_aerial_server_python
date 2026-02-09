# Repository Guidelines

## 项目结构与模块组织
- `main.py` 是 QUIC/WebTransport 服务入口，负责启动采集与传输服务。
- `service/` 是核心逻辑：`connection/`（协议/会话/路由）、`controller/`（采集与拉取流程）、`plugin/`（注册表与模型），以及 `repository/`、`database/`、`robot/`。
- `handler/` 放置请求/流处理器，例如 `broadcast.py`。
- `plugin/` 放置具体插件实现（如 `openai/`、`sqlite/`、`webdav/`）。
- `cert/` 保存 TLS 证书，路径需与 `main.py` 一致。
- `test/` 放置可直接运行的测试脚本，如 `test_fetch_playback.py`。

## 构建、测试与开发命令
- `uv sync`：安装 `pyproject.toml`/`uv.lock` 依赖（推荐使用 uv）。
- `uv run python main.py`：使用 uv 环境启动服务。
- `python main.py`：在已激活的虚拟环境中启动服务。
- `python test/test_fetch_playback.py`：运行播放回放测试（需要可用音频设备）。

## 编码风格与命名约定
- Python 4 空格缩进；函数/变量使用 `snake_case`，类使用 `PascalCase`。
- 模块/文件名保持小写（例：`service/controller/fetch.py`）。
- 优先使用类型注解，复用 `service/*/interface` 中的枚举与数据类。

## 测试指南
- 测试脚本位于 `test/`，命名为 `test_*.py`。
- 当前以可运行脚本为主，新增功能请补充脚本或提供手动验证命令。

## 提交与 Pull Request 指南
- 提交信息多为简短中文摘要（如“优化…”，“简单…”），请保持同样风格。
- PR 需说明目的、影响模块、验证方式（命令 + 结果）。
- 若修改证书路径或设备索引等配置，请在 PR 中注明。

## 配置与安全提示
- QUIC 启动依赖 `cert/` 中证书，勿提交真实生产密钥。
- 音频设备索引与环境有关，变更默认值请同步记录。
