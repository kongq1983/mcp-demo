import httpx
import asyncio

async def probe():
    base_url = "http://192.168.0.8:8000"
    paths = ["/", "/sse", "/mcp", "/messages"]
    print(f"正在探测服务器 {base_url} ...")
    
    async with httpx.AsyncClient() as client:
        for path in paths:
            url = f"{base_url}{path}"
            try:
                # 尝试 GET 和 POST
                resp_get = await client.get(url, timeout=2.0)
                print(f"GET  {url} -> {resp_get.status_code}")
                
                resp_post = await client.post(url, timeout=2.0)
                print(f"POST {url} -> {resp_post.status_code}")
            except Exception as e:
                print(f"ERR  {url} -> {e}")

if __name__ == "__main__":
    asyncio.run(probe())
