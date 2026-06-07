# MCP Server Demo

本项目是一个基于 `FastMCP` (v3.0.0) 构建的 MCP 服务端示例，提供天气预报和面积计算两个工具。

## 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐)

## 安装依赖

在项目根目录下运行：

```bash
uv sync
```

或者使用 `uv add` 安装特定版本：

```bash
uv add fastmcp==3.0.0
```

## 运行服务端

### 1. 标准模式 (STDIO)

此模式通常用于与 MCP 客户端（如 Claude Desktop）集成：

```bash
uv run python main.py
```

### 2. 开发/调试模式 (Inspector)

FastMCP 提供了一个内置的调试界面，可以在浏览器中测试工具：

```bash
fastmcp run main.py:mcp
fastmcp run main.py:mcp --host 192.168.0.8 --port 8000
fastmcp run main.py:mcp --log-level DEBUG
```
启动后，访问终端输出的本地地址（通常是 `http://localhost:8000`）即可进行可视化测试。

## 提供工具

1.  `get_weather(city: str)`: 获取模拟的天气信息。
2.  `calculate_area(width: float, length: float)`: 计算长方形面积。
