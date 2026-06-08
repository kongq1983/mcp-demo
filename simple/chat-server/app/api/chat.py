import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from app.models.leave import ChatRequest
from app.core.agent import agent_manager

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """流式聊天接口 (SSE)"""
    if not agent_manager.agent:
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
            async for chunk in agent_manager.agent.astream({"messages": messages}, stream_mode="messages"):
                msg, _ = chunk
                if isinstance(msg, AIMessage) and msg.content:
                    yield f"data: {json.dumps({'content': msg.content})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
