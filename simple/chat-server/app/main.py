from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, leave
from app.core.agent import agent_manager

def create_app() -> FastAPI:
    app = FastAPI(title="Chat Server for MCP (Modular)")

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(chat.router)
    app.include_router(leave.router)

    @app.on_event("startup")
    async def startup_event():
        await agent_manager.initialize()

    return app

app = create_app()
