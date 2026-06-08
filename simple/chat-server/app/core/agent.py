from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from app.core import config
class AgentManager:
    def __init__(self):
        self.llm = None
        self.agent = None

    async def initialize(self):
        # 1. 初始化 LLM
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            openai_api_key=config.OPENAI_API_KEY,
            openai_api_base=config.OPENAI_API_BASE,
            streaming=True
        )

        # 2. 初始化 MCP 客户端
        server_config = {
            "mcp-server": {
                "url": config.MCP_SERVER_URL,
                "transport": "http" 
            }
        }
        
        client = MultiServerMCPClient(server_config)
        try:
            mcp_tools = await client.get_tools()
            
            # 3. 创建系统提示词 (彻底实现通用化)
            today = datetime.now().strftime("%Y-%m-%d")
            system_message = SystemMessage(
                content=(
                    f"今天是 {today}。\n"
                    "你是一个全能助手。请优先使用提供的工具来满足用户的需求。\n"
                    "仔细阅读每个工具的描述，并严格遵守工具描述中的规则。"
                )
            )

            # 4. 创建 Agent
            self.agent = create_react_agent(self.llm, mcp_tools, prompt=system_message)
            print("Agent 启动成功，已连接并同步 MCP 插件能力。")
        except Exception as e:
            print(f"Agent 初始化失败: {e}")
            raise e

# 全局单例
agent_manager = AgentManager()
