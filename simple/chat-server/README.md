# Chat Server

这是一个基于 FastAPI 和 LangChain 的聊天后端，支持流式输出 (SSE)，并集成了 MCP (Model Context Protocol) 工具。

## 功能特性

- **流式对话**: 使用 Server-Sent Events (SSE) 实现打字机效果。
- **MCP 集成**: 自动连接并调用 MCP 服务器提供的工具（如天气查询、面积计算）。
- **智能 Agent**: 使用 LangGraph 的 React Agent 处理复杂逻辑。
- **请假处理**: 特化的请假逻辑，支持前端表单触发。

## 快速开始

### 1. 安装依赖

推荐使用 [uv](https://github.com/astral-sh/uv) 管理 Python 环境：

```bash
uv sync
```

或者使用 pip:

```bash
pip install fastapi uvicorn langchain langchain-openai langgraph python-dotenv
```

### 2. 配置环境变量

在 `chat-server` 目录下创建 `.env` 文件：

```env
ZHI_PU_AI_API_KEY=你的智谱AI秘钥
```

### 3. 启动服务

```bash
uv run main.py
```

服务器将运行在 `http://localhost:8001`。

## 接口说明

- `POST /chat`: 聊天接口，接收 `{message, history}`，返回流式 SSE 数据。
- `POST /leave/submit`: 请假提交接口，接收 `{name, date, reason}`。
