import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

# 加载环境变量
load_dotenv()

# 禁用代理，防止干扰本地/内网连接
os.environ["NO_PROXY"] = "192.168.0.8,localhost,127.0.0.1"

async def main():
    # 1. 初始化大模型 (使用智谱 AI)
    llm = ChatOpenAI(
        model="GLM-4.7-Flash",
        openai_api_key=os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )

    # 2. 初始化 MCP 客户端并连接服务器
    # 注意：MultiServerMCPClient 接收服务器配置字典
    server_config = {
        "mcp-server": {
            "url": "http://192.168.0.8:8000/mcp",
            "transport": "http" 
        }
    }
    
    print(f"正在尝试连接 MCP 服务器: {server_config['mcp-server']['url']} ...")
    client = MultiServerMCPClient(server_config)
    
    try:
        # 获取所有可用工具
        all_tools = await client.get_tools()
    except Exception as e:
        print(f"\n[错误] 无法连接到 MCP 服务器: {e}")
        print("请检查：")
        print(f"1. MCP 服务器是否已在 {server_config['mcp-server']['url']} 启动？")
        print("2. 网络连接是否正常，防火墙是否允许访问该端口？")
        print("3. 如果服务器在本地运行，尝试将 IP 改为 127.0.0.1 再次测试。")
        return
    
    # 3. 过滤工具：只保留计算面积和天气预报相关的工具
    # 假设工具名称中包含 'area' 或 'weather'，或者中文 '面积' 或 '天气'
    filtered_tools = [
        tool for tool in all_tools 
        if any(keyword in tool.name.lower() for keyword in ["area", "weather", "面积", "天气"])
    ]
    
    if not filtered_tools:
        print("警告: 未能在服务器上找到面积计算或天气预报相关的工具。")
    else:
        print(f"已加载工具: {[t.name for t in filtered_tools]}")

    # 4. 创建系统提示词，限制功能范围
    system_message = SystemMessage(
        content=(
            "你是一个助手，专门负责计算面积和查询天气预报。"
            "你只能通过调用提供的工具来回答关于『面积计算』或『天气预报』的问题。"
            "对于任何其他话题或请求，请礼貌地回答：『抱歉，我目前只支持计算面积和获取天气预报。』"
            "请直接给出答案，不要涉及无关信息。"
        )
    )

    # 5. 创建 Agent
    agent = create_react_agent(llm, filtered_tools, prompt=system_message)
    print("\n=== Agent 已启动 ===")
    print("提示：本助手仅支持计算面积和获取天气预报。输入 'exit' 或 'quit' 退出。")

    while True:
        try:
            user_input = input("\n用户输入 > ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue

            # 运行 Agent
            # langgraph agent 返回的是一个字典，包含 messages 序列
            result = await agent.ainvoke({"messages": [("user", user_input)]})
            
            # 打印最后一条消息（AI 的回复）
            print(f"助手回复: {result['messages'][-1].content}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
