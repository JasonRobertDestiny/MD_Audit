# API请求模型
from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """文件分析请求模型"""
    keywords: Optional[list[str]] = Field(
        None,
        max_items=10,
        description="用户关键词列表（最多10个）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": ["Python", "SEO", "Markdown"]
            }
        }
