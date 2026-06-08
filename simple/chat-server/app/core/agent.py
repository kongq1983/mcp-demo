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
            
            # 3. 创建系统提示词 (强化意图识别)
            today = datetime.now().strftime("%Y-%m-%d")
            system_message = SystemMessage(
                content=(
                    f"今天是 {today}，当前时间参考此日期。\n"
                    "你是一个全能助手，负责处理面积计算、天气查询和行政请假流程。\n"
                    "【核心规范】\n"
                    "1. 当用户表达『请假』意图时，你必须且只能通过调用 'open_leave_form' 工具来响应。\n"
                    "2. 请从对话中精准提取：请假人(applicant)、开始时间(start_time)、结束时间(end_time)、类型(leave_type)和原因(reason)。\n"
                    "3. 相对时间转换：如果用户说『昨天』，请基于 {today} 计算出具体日期。时间格式必须符合 ISO 8601 (YYYY-MM-DDTHH:mm)。\n"
                    "4. 不要只通过文字回复，必须调用工具。"
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
