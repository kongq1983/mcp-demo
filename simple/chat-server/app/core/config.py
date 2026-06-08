import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 代理设置
os.environ["NO_PROXY"] = "192.168.0.8,127.0.0.1,localhost"

# 模型配置
MODEL_NAME = "GLM-4.7-Flash"
OPENAI_API_KEY = os.getenv("ZHI_PU_AI_API_KEY") or "dummy_key"
OPENAI_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"

# MCP 服务器配置
MCP_SERVER_URL = "http://192.168.0.8:8000/mcp"
