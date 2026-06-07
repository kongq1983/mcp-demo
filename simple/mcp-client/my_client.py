import asyncio
from fastmcp import Client

# client = Client("http://127.0.0.1:8000/mcp")
client = Client("http://192.168.0.8:8000/mcp")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("get_weather", arguments={"city": "北京"})
        print(result)
        print(f"weather返回结果: {result.content[0].text}")

async def calc_area(width: float, length: float):
    async with client:
        result = await client.call_tool("calculate_area", arguments={"width": width, "length": length})
        print(result)
        print(f"area返回结果: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(call_tool("Ford"))
    asyncio.run(calc_area(10.0, 20.0))