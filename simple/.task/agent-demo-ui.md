# agent-demo-ui



```bash
## 1. Project Setup
本项目是agent-demo-ui端，需要带用户交互的输入框界面，具体都在这里交互

- 使用 `uv init` 初始化项目并创建虚拟环境
- 使用 `uv add` 添加必要的依赖（如有）
- 使用langchain来做例子
- mcp-client使用from langchain_mcp_adapters.client import MultiServerMCPClient
- 通过http方式连接mcp
- mcp服务器http://192.168.0.8:8000/mcp
- 本项目，需要1个交互界面，而不是终端交互，类似于chatgpt界面

- 验证通过 `uv run python main.py` 能够启动程序
- 带readme.md文件，里面写本项目环境文档，要包括启动等相关命令
- 提示词只支持计算面积和获取天气预报，通过mcp去调用，其他的就说不支持
- 写的代码，放在agent-demo-ui目录下
```



## 相关版本参考

```bash
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.28.1",
    "langchain>=1.3.4",
    "langchain-openai>=1.2.2",
    "mcp>=1.27.2",
    "python-dotenv>=1.2.2",
]
```





## 初始化大模型 

```
llm = ChatOpenAI(
    model="GLM-4.7-Flash",
    openai_api_key=os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)
```