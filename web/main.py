# FastAPI主应用
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
from pathlib import Path

from web.api import analyze, history, health


# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("md_audit_web")

# 创建FastAPI应用
app = FastAPI(
    title="MD Audit Web API",
    description="Markdown SEO诊断工具Web API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 速率限制器
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS中间件（安全的域名白名单）
# 从环境变量读取允许的源，默认仅本地开发
allowed_origins = os.getenv(
    "MD_AUDIT_ALLOWED_ORIGINS",
    "http://localhost:8000,http://localhost:5173,http://127.0.0.1:8000,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # 预检请求缓存10分钟
)

# Gzip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path} - {request.client.host}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response

# 注册API路由
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(health.router)

# 挂载静态文件（前端构建产物）
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
else:
    logger.warning(f"静态文件目录不存在：{static_dir}")

# 根路径（欢迎页）
@app.get("/api/")
async def root():
    return {
        "message": "MD Audit Web API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# 定时清理临时文件
from web.services.file_service import FileService
import asyncio


async def cleanup_task():
    """后台任务：每小时清理临时文件"""
    file_service = FileService()
    while True:
        await asyncio.sleep(3600)  # 1小时
        logger.info("开始清理临时文件...")
        file_service.cleanup_old_files(max_age_hours=24)
        logger.info("临时文件清理完成")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("MD Audit Web服务启动中...")

    # 启动后台清理任务
    asyncio.create_task(cleanup_task())

    logger.info("MD Audit Web服务已启动 ✅")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("MD Audit Web服务已停止")
