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
            all_tools = await client.get_tools()
            # 过滤工具
            filtered_tools = [
                tool for tool in all_tools 
                if any(keyword in tool.name.lower() for keyword in ["area", "weather", "面积", "天气"])
            ]
            
            # 3. 创建系统提示词
            today = datetime.now().strftime("%Y-%m-%d")
            system_message = SystemMessage(
                content=(
                    f"今天是 {today}。\n"
                    "你是一个助手，专门负责计算面积、查询天气预报以及处理请假申请。\n"
                    "1. 对于『面积计算』或『天气预报』，请调用提供的工具。\n"
                    "2. 当用户表达『请假』意图时，你必须在回复中包含且仅包含触发码：[[LEAVE_FORM:日期]]，日期格式 YYYY-MM-DD。\n"
                    "3. 对于其他话题，礼貌拒绝并说明功能范围。\n"
                    "请直接给出答案，不要涉及无关信息。"
                )
            )

            # 4. 创建 Agent
            self.agent = create_react_agent(self.llm, filtered_tools, prompt=system_message)
            print("Agent 启动成功，已连接至 MCP 服务器。")
        except Exception as e:
            print(f"Agent 初始化失败: {e}")
            raise e

# 全局单例
agent_manager = AgentManager()
