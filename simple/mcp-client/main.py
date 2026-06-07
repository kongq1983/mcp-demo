import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # 获取服务端 main.py 的绝对路径
    # 假设服务端在 ../mcp-server/main.py
    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp-server", "main.py"))
    
    # 定义服务端启动参数
    # 使用 uv run 确保环境正确
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", server_path],
        env=os.environ.copy()
    )

    print(f"正在连接到 MCP 服务端: {server_path}...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            print("连接已建立，正在列出可用工具...")

            # 列出工具
            tools = await session.list_tools()
            print(f"发现工具: {[tool.name for tool in tools.tools]}")

            # 调用天气预报工具
            print("\n--- 调用 get_weather ---")
            weather_result = await session.call_tool("get_weather", arguments={"city": "北京"})
            print(f"返回结果: {weather_result.content[0].text}")

            # 调用面积计算工具
            print("\n--- 调用 calculate_area ---")
            area_result = await session.call_tool("calculate_area", arguments={"width": 10.5, "length": 20.0})
            print(f"返回结果: {area_result.content[0].text}")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except Exception as e:
        print(f"客户端运行出错: {e}")
