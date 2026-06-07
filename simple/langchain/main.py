import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

# 加载环境变量
load_dotenv()

# 禁用代理，防止干扰本地/内网连接
os.environ["NO_PROXY"] = "192.168.0.8,localhost,127.0.0.1"

async def main():
    # 检查 API Key
    if not os.getenv("ZHI_PU_AI_API_KEY"):
        print("注意: 未检测到 ZHI_PU_AI_API_KEY，程序将无法正常调用大模型。")
        print("请在 .env 文件中设置 ZHI_PU_AI_API_KEY 以完成实际调用。")

    # 1. 配置 MCP 服务器 URL (使用 SSE)
    mcp_url = "http://192.168.0.8:8000/mcp"
    print(f"正在配置远程 MCP 服务器: {mcp_url}...")

    # 2. 初始化 MultiServerMCPClient 并配置连接
    # 实例化客户端
    client = MultiServerMCPClient({
        "mcp-server": {
            "transport": "http",
            "url":mcp_url,
        }
    })
    
    try:
        print("正在获取并转换工具...")
        # 异步获取转换后的 LangChain 工具
        lc_tools = await client.get_tools()
        print(f"成功加载工具: {[t.name for t in lc_tools]}")

        # 3. 初始化智谱 AI 模型 (使用 OpenAI 兼容接口)
        llm = ChatOpenAI(
            model="GLM-4.7-Flash",
            openai_api_key=os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
        )

        # 4. 构建 LangChain Agent
        print("正在创建 Agent...")
        agent = create_agent(
            model=llm,
            tools=lc_tools,
            system_prompt="你是一个有用的助手。你可以调用工具来获取实时信息或执行计算。"
        )

        # 5. 执行测试任务
        if not os.getenv("ZHI_PU_AI_API_KEY"):
            print("\n跳过实际调用测试，因为 API Key 未设置。")
            return

        print("\n=== 测试任务 1: 查询天气 ===")
        try:
            result1 = await agent.ainvoke({"messages": [("human", "北京今天天气怎么样？")]})
            print(f"回答: {result1['messages'][-1].content}")
        except Exception as e:
            print(f"任务 1 运行出错: {e}")

        print("\n=== 测试任务 2: 计算长方形面积 ===")
        try:
            result2 = await agent.ainvoke({"messages": [("human", "一个长 12.5 米，宽 8 米的长方形面积是多少？")]})
            print(f"回答: {result2['messages'][-1].content}")
        except Exception as e:
            print(f"任务 2 运行出错: {e}")

    except Exception:
        import traceback
        print("连接或工具获取失败:")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"程序执行失败: {e}")
