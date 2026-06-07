# MCP Client Demo

本项目是一个基于官方 `mcp` SDK 构建的 MCP 客户端示例，用于连接并调用 `mcp-server` 提供的工具。

## 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐)

## 安装依赖

在项目根目录下运行：

```bash
uv sync
```

## 运行客户端

在运行客户端之前，请确保 `mcp-server` 目录下的环境已准备就绪。

```bash
uv run python main.py
```

## 运行逻辑

1.  客户端会自动定位到同级目录下的 `../mcp-server/main.py`。
2.  通过 `stdio` 传输协议启动并连接服务端。
3.  自动列出服务端支持的工具。
4.  演示调用 `get_weather` 和 `calculate_area` 工具。
