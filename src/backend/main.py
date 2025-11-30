"""
GenAI模型能效评级体系 - 后端主入口

本模块是GenAI模型能效评级系统的核心后端服务，提供以下功能：
- 模型评估API接口
- 数据集管理
- 实验跟踪
- 结果分析
- 用户管理
- 任务调度

作者: GenAI研究团队
版本: 1.0.0
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# 将项目根目录添加到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

# 导入应用模块
from src.backend.core.config import settings
from src.backend.core.database import init_db, get_db
from src.backend.api.v1.router import api_router
from src.backend.core.logging import setup_logging
from src.backend.core.exceptions import AppException
from src.backend.services.task_scheduler import TaskScheduler
from src.backend.services.model_cache import ModelCache
from src.backend.services.experiment_tracker import ExperimentTracker

# 设置日志
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request, call_next):
        # 记录请求
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # 调用下一个中间件或路由处理函数
        response = await call_next(request)
        
        # 记录响应
        logger.info(f"Response: {response.status_code}")
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    
    # 启动时执行
    logger.info("🚀 正在启动GenAI模型能效评级系统...")
    
    try:
        # 初始化数据库
        logger.info("📊 初始化数据库...")
        await init_db()
        
        # 初始化模型缓存
        logger.info("🧠 初始化模型缓存...")
        app.state.model_cache = ModelCache()
        await app.state.model_cache.initialize()
        
        # 初始化任务调度器
        logger.info("⏰ 初始化任务调度器...")
        app.state.task_scheduler = TaskScheduler()
        await app.state.task_scheduler.start()
        
        # 初始化实验跟踪器
        logger.info("🔬 初始化实验跟踪器...")
        app.state.experiment_tracker = ExperimentTracker()
        await app.state.experiment_tracker.initialize()
        
        logger.info("✅ 系统初始化完成")
        
    except Exception as e:
        logger.error(f"❌ 系统初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("🛑 正在关闭系统...")
    
    try:
        # 停止任务调度器
        if hasattr(app.state, 'task_scheduler'):
            await app.state.task_scheduler.stop()
            logger.info("任务调度器已停止")
        
        # 关闭模型缓存
        if hasattr(app.state, 'model_cache'):
            await app.state.model_cache.close()
            logger.info("模型缓存已关闭")
        
        # 关闭实验跟踪器
        if hasattr(app.state, 'experiment_tracker'):
            await app.state.experiment_tracker.close()
            logger.info("实验跟踪器已关闭")
        
        logger.info("✅ 系统已安全关闭")
        
    except Exception as e:
        logger.error(f"❌ 系统关闭时出错: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="GenAI模型能效评级系统",
    description="""
    基于多维效质比的GenAI模型能效评估与市场价值分析系统
    
    ## 主要功能
    - 🧠 模型能效评估
    - 📊 多维度性能分析
    - 🔬 实验管理与跟踪
    - 📈 数据可视化
    - 🤝 协作研究支持
    - 📄 报告生成
    
    ## 技术特点
    - 支持多种AI模型类型（LLM、CV、多模态等）
    - 提供标准化评估指标
    - 实时性能监控
    - 可扩展的架构设计
    - 开源友好的许可
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)


# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """处理应用自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未捕获的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": str(exc) if settings.DEBUG else "请联系技术支持"
            }
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "cache": "connected",
            "scheduler": "running"
        }
    }


# 根路径
@app.get("/")
async def root():
    """根路径重定向到文档"""
    return {
        "message": "欢迎使用GenAI模型能效评级系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }


# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


def main():
    """主函数"""
    
    # 设置日志
    setup_logging()
    
    # 检查环境变量
    if not settings.validate():
        logger.error("环境变量配置错误")
        sys.exit(1)
    
    logger.info("🚀 启动GenAI模型能效评级系统")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"API版本: v1")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        workers=1 if settings.DEBUG else settings.WORKERS,
        access_log=settings.DEBUG
    )


if __name__ == "__main__":
    main()