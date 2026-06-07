# LangChain MCP 演示项目

本项目展示了如何使用 LangChain (1.0+) 框架集成智谱 AI 大模型，并通过 MCP (Model Context Protocol) 协议调用外部工具。

## 功能特性

- 使用 `uv` 进行依赖管理。
- 集成智谱 AI (`glm-4`) 作为核心 LLM。
- 动态加载并调用 `mcp-server` 中定义的工具（如天气查询、面积计算）。
- 使用 LangChain 的 OpenAI Tools Agent 模式进行工具调用。

## 环境准备

1. **安装 uv**: 如果尚未安装，请参考 [uv 官网](https://github.com/astral-sh/uv)。
2. **获取智谱 AI API Key**: 前往 [智谱 AI 开放平台](https://open.bigmodel.cn/) 获取。

## 配置

在 `langchain` 目录下创建 `.env` 文件，并填写您的 API Key：

```env
ZHIPUAI_API_KEY=您的智谱API密钥
```

## 启动说明

确保您处于项目根目录下，或者已进入 `langchain` 目录。

### 1. 安装依赖

```bash
uv sync
```

### 2. 运行程序

```bash
uv run main.py
```

程序会自动启动 `mcp-server`（位于 `../mcp-server/main.py`），并执行以下两个测试任务：
1. 查询北京的天气。
2. 计算一个长方形的面积。

## 项目结构

- `main.py`: 主程序，负责连接 MCP 服务器、转换工具、初始化 LLM 并执行 Agent。
- `pyproject.toml`: 项目配置文件和依赖定义。
- `.env`: 环境变量配置（需手动创建）。
```
