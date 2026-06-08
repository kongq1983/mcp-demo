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
                # 1. 处理文本内容
                if hasattr(msg, "content") and msg.content:
                    yield f"data: {json.dumps({'content': msg.content})}\n\n"
                
                # 2. 处理工具调用 (支持完整 tool_calls 和流式 tool_call_chunks)
                tool_calls = []
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls = msg.tool_calls
                elif hasattr(msg, "tool_call_chunks") and msg.tool_call_chunks:
                    # 简单处理：如果是分片，我们只取第一个完整的分片名称和参数
                    # 在实际流式中，参数是分段到达的，这里我们等待参数收集完毕或处理完整调用
                    tool_calls = msg.tool_call_chunks

                if tool_calls:
                    for tc in tool_calls:
                        # 兼容处理：chunks 的格式可能略有不同
                        name = tc.get("name")
                        args = tc.get("args") or tc.get("arguments")
                        
                        if name and name.startswith("open_"):
                            print(f"检测到 UI 触发工具: {name}, 参数: {args}")
                            ui_type = name.replace("open_", "").replace("_form", "")
                            # 如果 args 是字符串（某些模型会这样），尝试解析
                            if isinstance(args, str):
                                try: args = json.loads(args)
                                except: pass
                            
                            if args:
                                action_data = {"type": ui_type, "data": args}
                                trigger_str = f"[[ACTION:{json.dumps(action_data)}]]"
                                yield f"data: {json.dumps({'content': trigger_str})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
