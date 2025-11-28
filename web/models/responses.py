# API响应模型
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error_code: str = Field(..., description="错误码")
    message: str = Field(..., description="用户友好的错误信息")
    suggestion: str = Field(..., description="解决建议")
    details: Optional[str] = Field(None, description="技术细节（开发模式）")


class AnalyzeResponse(BaseModel):
    """文件分析响应模型"""
    report: dict = Field(..., description="SEO诊断报告")
    history_id: str = Field(..., description="历史记录ID")


class HistoryItem(BaseModel):
    """历史记录项模型"""
    id: str = Field(..., description="唯一记录ID")
    timestamp: datetime = Field(..., description="诊断时间")
    file_name: str = Field(..., description="文件名")
    total_score: float = Field(..., ge=0, le=100, description="总分")
    severity_counts: dict[str, int] = Field(
        default_factory=lambda: {"error": 0, "warning": 0, "success": 0},
        description="问题数量统计"
    )


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    items: list[HistoryItem] = Field(default_factory=list)
    total: int = Field(..., description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=100, description="每页数量")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态（healthy/unhealthy）")
    version: str = Field(..., description="Web服务版本")
    analyzer_version: str = Field(..., description="Analyzer版本")
    ai_enabled: bool = Field(..., description="AI分析是否启用")
