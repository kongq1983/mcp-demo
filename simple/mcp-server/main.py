from fastmcp import FastMCP
import random

# 创建 FastMCP 实例
mcp = FastMCP("MCP Demo Server")

@mcp.tool()
def get_weather(city: str) -> str:
    """
    获取指定城市的天气预报。
    
    :param city: 城市名称 (例如: "北京", "Shanghai")
    """
    weathers = ["晴朗", "多云", "小雨", "大风", "阴天"]
    temp = random.randint(-10, 35)
    return f"{city} 的天气预计为: {random.choice(weathers)}，气温: {temp}℃。"

@mcp.tool()
def calculate_area(width: float, length: float) -> str:
    """
    计算长方形的面积。
    
    :param width: 宽度
    :param length: 长度
    """
    area = width * length
    return f"宽度为 {width}，长度为 {length} 的长方形面积为: {area:.2f}"

if __name__ == "__main__":
    # 运行 MCP 服务器，默认使用 stdio 传输
    mcp.run(
        transport="http",
        # host="127.0.0.1",
        host="192.168.0.8",
        port=8000
    )

    # fastmcp run my_server.py:mcp --transport http --port 8000