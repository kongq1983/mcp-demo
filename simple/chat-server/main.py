import asyncio
import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 加载环境变量
load_dotenv()

# 禁用代理，防止干扰本地/内网连接
os.environ["NO_PROXY"] = "192.168.0.8,127.0.0.1,localhost"

app = FastAPI(title="Chat Server for MCP")

# 配置 CORS，允许 Vue 前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 模型和 Agent 全局状态 ---
llm = None
agent = None

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

class LeaveRequest(BaseModel):
    name: str
    date: str
    reason: str

@app.on_event("startup")
async def startup_event():
    """服务器启动时初始化连接"""
    global llm, agent
    
    # 1. 初始化 LLM
    llm = ChatOpenAI(
        model="GLM-4.7-Flash",
        openai_api_key=os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        streaming=True # 启用流式
    )

    # 2. 初始化 MCP 客户端
    server_config = {
        "mcp-server": {
            "url": "http://192.168.0.8:8000/mcp",
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
        agent = create_react_agent(llm, filtered_tools, prompt=system_message)
        print("Agent 启动成功，已连接至 MCP 服务器。")
    except Exception as e:
        print(f"初始化失败: {e}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """流式聊天接口 (SSE)"""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent 未就绪")

    # 转换历史记录
    messages = []
    for m in request.history:
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=request.message))

    async def generate():
        try:
            # 使用 astream 处理流式输出
            # 注意：create_react_agent (LangGraph) 的 astream 返回的是状态更新
            # 我们需要捕获其中的消息内容
            async for chunk in agent.astream({"messages": messages}, stream_mode="messages"):
                # chunk 是 (message, metadata) 元组
                msg, _ = chunk
                if isinstance(msg, AIMessage) and msg.content:
                    # 将内容以 SSE 格式发送
                    # 这里为了前端方便，直接发送字符串内容，前缀为 data:
                    yield f"data: {json.dumps({'content': msg.content})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/leave/submit")
async def submit_leave(request: LeaveRequest):
    """请假提交接口"""
    print(f"收到请假申请: {request.name}, {request.date}, {request.reason}")
    # 模拟业务逻辑
    if not request.name or not request.date:
        return {"success": False, "message": "姓名和日期不能为空"}
    
    return {
        "success": True, 
        "message": f"✅ 申请已提交！已成功为 {request.name} 预约了 {request.date} 的请假。"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
