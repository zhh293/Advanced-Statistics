"""FastAPI 主入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS
from database import init_db
from routers import accidents, analysis, mining, crawl
from tasks.crawl_scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时
    init_db()
    start_scheduler()
    yield
    # 关闭时
    stop_scheduler()


app = FastAPI(
    title="交通事故数据挖掘分析平台",
    description="基于网络数据的交通违法与事故案例挖掘分析系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(accidents.router)
app.include_router(analysis.router)
app.include_router(mining.router)
app.include_router(crawl.router)


@app.get("/")
def root():
    return {"message": "交通事故数据挖掘分析平台", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
