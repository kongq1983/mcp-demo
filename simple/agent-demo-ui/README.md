# Agent Demo UI

本项目提供了一个基于网页的智能助手界面，用户可以通过类 ChatGPT 的 UI 进行交互。

## 功能特点
- **现代 UI**：基于 Streamlit 构建，支持实时对话。
- **功能专注**：仅支持面积计算和天气预报查询。
- **MCP 集成**：通过 LangChain 适配器连接远程 MCP 工具服务器。

## 环境准备

1. **安装 uv**:
   确保您的系统中已安装 `uv`。

2. **配置环境变量**:
   在 `agent-demo-ui` 目录下创建 `.env` 文件：
   ```bash
   ZHI_PU_AI_API_KEY=您的API密钥
   ```

## 启动步骤

运行以下命令启动网页界面：
```bash
uv run python main.py
```
程序启动后，会自动在浏览器中打开 `http://localhost:8501`。

## 注意事项
- 请确保 MCP 工具服务器（位于 `mcp-server` 目录）已先行启动。
- 默认连接地址为 `http://192.168.0.8:8000/`。
