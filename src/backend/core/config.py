"""
GenAI模型能效评级体系 - 核心配置模块

本模块负责管理系统的所有配置项，包括：
- 数据库配置
- API配置
- 模型评估配置
- 缓存配置
- 日志配置
- 安全配置

作者: GenAI研究团队
版本: 1.0.0
"""

import os
import secrets
from typing import List, Optional, Union
from pydantic import BaseSettings, validator, AnyHttpUrl, EmailStr
from pathlib import Path


class Settings(BaseSettings):
    """系统配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "GenAI模型能效评级系统"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于多维效质比的GenAI模型能效评估与市场价值分析系统"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # API配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    ALGORITHM: str = "HS256"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """组装CORS源列表"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost/genai_power_evaluation"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis配置（用于缓存和会话）
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    REDIS_TIMEOUT: int = 5
    
    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/json",
        "text/csv",
        "application/parquet",
        "application/zip",
        "text/plain"
    ]
    
    # 模型配置
    MODEL_CACHE_DIR: str = "cache/models"
    MODEL_MAX_SIZE: int = 1024 * 1024 * 1024  # 1GB
    MODEL_TIMEOUT: int = 300  # 5分钟
    HUGGINGFACE_CACHE_DIR: str = "cache/huggingface"
    
    # Hugging Face配置
    HUGGINGFACE_TOKEN: Optional[str] = None
    HUGGINGFACE_ENDPOINT: str = "https://huggingface.co"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_TIMEOUT: int = 60
    
    # 评估配置
    EVALUATION_BATCH_SIZE: int = 32
    EVALUATION_MAX_WORKERS: int = 4
    EVALUATION_TIMEOUT: int = 3600  # 1小时
    EVALUATION_RESULT_CACHE_TTL: int = 86400  # 24小时
    
    # 性能指标配置
    PERFORMANCE_METRICS = {
        "accuracy": {"weight": 0.25, "threshold": 0.8},
        "efficiency": {"weight": 0.25, "threshold": 0.7},
        "robustness": {"weight": 0.20, "threshold": 0.75},
        "fairness": {"weight": 0.15, "threshold": 0.8},
        "sustainability": {"weight": 0.15, "threshold": 0.7}
    }
    
    # 实验配置
    EXPERIMENT_TRACKING_ENABLED: bool = True
    EXPERIMENT_TRACKING_URI: str = "http://localhost:5000"
    EXPERIMENT_ARTIFACT_LOCATION: str = "experiments"
    
    # MLflow配置
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_ARTIFACT_ROOT: str = "mlruns"
    MLFLOW_EXPERIMENT_NAME: str = "genai_power_evaluation"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_BACKUP_COUNT: int = 5
    
    # 监控配置
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    METRICS_PATH: str = "/metrics"
    
    # 通知配置
    EMAIL_ENABLED: bool = False
    EMAIL_SMTP_SERVER: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USERNAME: Optional[EmailStr] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[EmailStr] = None
    
    # 数据配置
    DATA_DIR: str = "data"
    RAW_DATA_DIR: str = "data/raw"
    PROCESSED_DATA_DIR: str = "data/processed"
    EXTERNAL_DATA_DIR: str = "data/external"
    
    # 结果配置
    RESULTS_DIR: str = "results"
    REPORTS_DIR: str = "reports"
    PLOTS_DIR: str = "plots"
    
    # 前端配置
    FRONTEND_URL: str = "http://localhost:3000"
    FRONTEND_BUILD_DIR: str = "../frontend/dist"
    
    # 测试配置
    TESTING: bool = False
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    # 安全头配置
    SECURITY_HEADERS_ENABLED: bool = True
    
    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # 文件上传配置
    UPLOAD_TEMP_DIR: str = "temp"
    UPLOAD_CLEANUP_INTERVAL: int = 3600  # 1小时
    
    # 模型服务配置
    MODEL_SERVICE_ENABLED: bool = True
    MODEL_SERVICE_TIMEOUT: int = 300  # 5分钟
    MODEL_SERVICE_MAX_CONCURRENT: int = 5
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1小时
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数
    
    # 异步任务配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    
    # Jupyter配置
    JUPYTER_ENABLED: bool = True
    JUPYTER_PORT: int = 8888
    JUPYTER_TOKEN: Optional[str] = None
    JUPYTER_NOTEBOOK_DIR: str = "notebooks"
    
    # 文档配置
    DOCS_ENABLED: bool = True
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # 版本配置
    API_VERSION: str = "v1"
    MODEL_VERSION: str = "1.0.0"
    
    # 合规配置
    GDPR_COMPLIANT: bool = True
    DATA_RETENTION_DAYS: int = 365
    
    # 备份配置
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    BACKUP_RETENTION_DAYS: int = 30
    
    # 验证配置
    def validate(self) -> bool:
        """验证配置的有效性"""
        
        # 检查必要的环境变量
        required_vars = [
            "SECRET_KEY",
            "DATABASE_URL"
        ]
        
        for var in required_vars:
            if not getattr(self, var):
                print(f"❌ 缺少必要的环境变量: {var}")
                return False
        
        # 检查目录是否存在
        directories = [
            self.UPLOAD_DIR,
            self.MODEL_CACHE_DIR,
            self.DATA_DIR,
            self.RESULTS_DIR,
            self.LOG_FILE.rsplit("/", 1)[0] if "/" in self.LOG_FILE else "logs"
        ]
        
        for dir_path in directories:
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"✅ 创建目录: {dir_path}")
                except Exception as e:
                    print(f"❌ 创建目录失败 {dir_path}: {e}")
                    return False
        
        # 验证数据库连接
        try:
            from sqlalchemy import create_engine
            engine = create_engine(self.DATABASE_URL)
            engine.connect().close()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
        
        # 验证Redis连接
        if self.CACHE_ENABLED:
            try:
                import redis
                redis_client = redis.from_url(self.REDIS_URL)
                redis_client.ping()
                print("✅ Redis连接成功")
            except Exception as e:
                print(f"❌ Redis连接失败: {e}")
                return False
        
        return True
    
    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 导出配置
__all__ = ["settings"]