import streamlit as st
import asyncio
import os
import sys
import subprocess
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 支持 uv run python main.py 启动 ---
if __name__ == "__main__" and not st.runtime.exists():
    print("正在启动网页界面...")
    # 如果不是由 streamlit 运行的，则调用 subprocess 运行 streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", __file__, "--server.port", "8501"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
    sys.exit()

# --- Streamlit 页面配置 ---
st.set_page_config(page_title="MCP 智能助手", page_icon="🤖", layout="centered")
st.title("🤖 MCP 智能助手")
st.caption("支持功能：面积计算、天气预报查询")

# 加载环境变量
load_dotenv()

# 禁用代理，防止干扰本地/内网连接
os.environ["NO_PROXY"] = "192.168.0.8,127.0.0.1,localhost"

# --- 核心逻辑 ---

@st.cache_resource
def get_agent_and_tools():
    """初始化 LLM 和 MCP Agent (单例模式)"""
    # 1. 初始化大模型
    llm = ChatOpenAI(
        model="GLM-4.7-Flash",
        openai_api_key=os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )

    # 2. 初始化 MCP 客户端
    # 匹配终端版验证成功的配置
    server_config = {
        "mcp-server": {
            "url": "http://192.168.0.8:8000/mcp",
            "transport": "http" 
        }
    }
    
    # 内部异步函数用于获取工具
    async def initialize():
        client = MultiServerMCPClient(server_config)
        try:
            all_tools = await client.get_tools()
            # 过滤工具
            filtered_tools = [
                tool for tool in all_tools 
                if any(keyword in tool.name.lower() for keyword in ["area", "weather", "面积", "天气"])
            ]
            return filtered_tools
        except Exception as e:
            st.error(f"连接 MCP 服务器失败: {e}")
            return []

    # Streamlit 运行在同步环境，需要处理异步调用
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    filtered_tools = loop.run_until_complete(initialize())

    # 3. 创建系统提示词
    system_message = SystemMessage(
        content=(
            "你是一个助手，专门负责计算面积和查询天气预报。"
            "你只能通过调用提供的工具来回答关于『面积计算』或『天气预报』的问题。"
            "对于任何其他话题或请求，请礼貌地回答：『抱歉，我目前只支持计算面积和获取天气预报。』"
            "请直接给出答案，不要涉及无关信息。"
        )
    )

    # 4. 创建 Agent
    if not filtered_tools:
        st.warning("未检测到有效工具，Agent 功能可能受限。")
    
    agent = create_react_agent(llm, filtered_tools, prompt=system_message)
    return agent

# 初始化 Agent
agent = get_agent_and_tools()

# --- 聊天界面 ---

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接收用户输入
if prompt := st.chat_input("您可以问我面积计算或天气预报的问题..."):
    # 添加用户消息到界面
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用 Agent 获取回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 转换历史消息为 LangChain 格式
                history = []
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "user":
                        history.append(HumanMessage(content=m["content"]))
                    else:
                        history.append(AIMessage(content=m["content"]))
                
                # 运行 Agent
                async def run_agent():
                    response = await agent.ainvoke({"messages": history + [HumanMessage(content=prompt)]})
                    return response["messages"][-1].content

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                full_response = loop.run_until_complete(run_agent())
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_msg = f"发生错误: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
