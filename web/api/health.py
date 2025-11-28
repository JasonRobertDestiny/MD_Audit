# 健康检查API
from fastapi import APIRouter
from web.models.responses import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    返回服务状态和版本信息
    """
    try:
        # 检查analyzer模块是否可导入
        from md_audit.analyzer import MarkdownSEOAnalyzer
        from md_audit.config import MarkdownSEOConfig

        # 检查配置是否有效
        config = MarkdownSEOConfig()
        ai_enabled = config.enable_ai_analysis and bool(config.llm_api_key)

        return HealthResponse(
            status="healthy",
            version="1.0.0",  # Web服务版本
            analyzer_version="1.0.0",  # Analyzer版本
            ai_enabled=ai_enabled
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            analyzer_version="unknown",
            ai_enabled=False
        )
