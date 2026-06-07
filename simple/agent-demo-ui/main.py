import streamlit as st
import asyncio
import os
import sys
import subprocess
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 模拟业务系统提交 ---
def submit_leave_request(name, date, reason):
    """模拟提交请假到业务系统"""
    if name and date and reason:
        return True, f"✅ 提交成功！已为 {name} 提交了 {date} 的请假申请。"
    return False, "❌ 提交失败：请确保所有信息填写完整。"

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
st.caption("支持功能：面积计算、天气预报查询、请假申请")

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
    today = datetime.now().strftime("%Y-%m-%d")
    system_message = SystemMessage(
        content=(
            f"今天是 {today}。\n"
            "你是一个助手，专门负责计算面积、查询天气预报以及处理请假申请。\n"
            "1. 对于『面积计算』或『天气预报』，请调用提供的工具。\n"
            "2. 当用户表达『请假』意图时（例如：我要请假、明天想请假），你必须引导用户填写表单。\n"
            "你必须在回复中包含且仅包含一个特殊触发码：[[LEAVE_FORM:日期]]，其中『日期』应为用户提到的日期（如：2026-06-08）或今天。\n"
            "3. 对于任何其他话题，请礼貌拒绝并说明你目前只支持上述三项功能。\n"
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

# --- 渲染消息函数 ---

def render_message(role, content, index):
    """渲染单条消息，支持解析特殊触发码并嵌入表单"""
    with st.chat_message(role):
        # 查找触发码 [[LEAVE_FORM:YYYY-MM-DD]]
        pattern = r"\[\[LEAVE_FORM:(.*?)\]\]"
        match = re.search(pattern, content)
        
        if match:
            # 分割文本，显示触发码之前的描述
            text_before = content[:match.start()].strip()
            if text_before:
                st.markdown(text_before)
            
            # 渲染表单
            date_val = match.group(1)
            form_key = f"leave_form_{index}"
            
            with st.container(border=True):
                st.markdown("### 📝 请假申请单")
                # 使用 session_state 存储提交状态，防止刷新消失
                success_key = f"submit_success_{index}"
                
                if success_key in st.session_state:
                    st.success(st.session_state[success_key])
                else:
                    with st.form(key=form_key):
                        name = st.text_input("申请人姓名")
                        leave_date = st.text_input("请假日期", value=date_val)
                        reason = st.text_area("请假原因")
                        submitted = st.form_submit_button("确认提交")
                        
                        if submitted:
                            success, msg = submit_leave_request(name, leave_date, reason)
                            if success:
                                st.session_state[success_key] = msg
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.markdown(content)

# --- 聊天界面 ---

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for i, message in enumerate(st.session_state.messages):
    render_message(message["role"], message["content"], i)

# 接收用户输入
if prompt := st.chat_input("计算面积、查天气，或者直接说‘我要请假’..."):
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
                
                # 渲染新回复
                render_message("assistant", full_response, len(st.session_state.messages))
                # 存储消息
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_msg = f"发生错误: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
