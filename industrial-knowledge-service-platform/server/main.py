import uvicorn
from fastapi import FastAPI
from routers import api_router
from server_config.database import get_db_manager
from server_config.settings import UVICORN_CONFIG
from services.agent_service import agent_manager

# 初始化 FastAPI 应用
app = FastAPI(
    title="工业知识服务平台",
    description="面向工业知识图谱与RAG服务的后端 API",
)

# 添加路由
app.include_router(api_router)

# 获取数据库连接
db_manager = get_db_manager()
driver = db_manager.driver


@app.on_event("shutdown")
def shutdown_event():
    """应用关闭时清理资源"""
    # 关闭所有Agent资源
    agent_manager.close_all()
    
    # 关闭Neo4j连接
    if driver:
        driver.close()
        print("已关闭Neo4j连接")


# 启动服务器
if __name__ == "__main__":
    uvicorn.run("main:app", **UVICORN_CONFIG)
