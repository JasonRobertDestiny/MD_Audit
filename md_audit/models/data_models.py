from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    """诊断问题严重程度"""
    CRITICAL = "critical"  # 严重影响SEO
    WARNING = "warning"    # 需要改进
    INFO = "info"         # 建议优化
    SUCCESS = "success"   # 符合最佳实践


class DiagnosticItem(BaseModel):
    """单个诊断项"""
    category: str = Field(..., description="类别：metadata/structure/keywords/ai_semantics")
    check_name: str = Field(..., description="检查项名称，如'title_length'")
    severity: SeverityLevel
    score: float = Field(..., ge=0, le=100, description="该项得分（0-100）")
    message: str = Field(..., description="问题描述或成功信息")
    suggestion: str = Field(default="", description="改进建议")
    current_value: Optional[str] = Field(default=None, description="当前值")
    expected_value: Optional[str] = Field(default=None, description="期望值")


class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    relevance_score: float = Field(..., ge=0, le=100, description="内容相关性（0-100）")
    depth_score: float = Field(..., ge=0, le=100, description="内容深度（0-100）")
    readability_score: float = Field(..., ge=0, le=100, description="可读性（0-100）")
    overall_feedback: str = Field(default="", description="综合评价")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议列表")


class SEOReport(BaseModel):
    """完整SEO诊断报告"""
    file_path: str
    total_score: float = Field(..., ge=0, le=100)

    # 分项得分
    metadata_score: float = Field(default=0, ge=0, le=30, description="元数据得分（满分30）")
    structure_score: float = Field(default=0, ge=0, le=25, description="结构得分（满分25）")
    keyword_score: float = Field(default=0, ge=0, le=20, description="关键词得分（满分20）")
    ai_score: float = Field(default=0, ge=0, le=25, description="AI语义得分（满分25）")

    # 详细诊断
    diagnostics: List[DiagnosticItem] = Field(default_factory=list)
    ai_analysis: Optional[AIAnalysisResult] = None

    # 提取的元数据
    extracted_keywords: List[str] = Field(default_factory=list, description="自动提取的关键词")
    user_keywords: List[str] = Field(default_factory=list, description="用户提供的关键词")

    @property
    def emoji_badge(self) -> str:
        """总分对应的emoji徽章"""
        if self.total_score < 40:
            return "🔴"
        elif self.total_score < 60:
            return "🟠"
        elif self.total_score < 80:
            return "🟡"
        else:
            return "🟢"


class ParsedMarkdown(BaseModel):
    """解析后的Markdown内容"""
    frontmatter: Dict[str, Any] = Field(default_factory=dict, description="YAML frontmatter")
    raw_content: str = Field(default="", description="去除frontmatter的Markdown正文")
    html_content: str = Field(default="", description="转换后的HTML")
    title: str = Field(default="", description="从frontmatter或H1提取的标题")
    description: str = Field(default="", description="从frontmatter提取的描述")
    h1_tags: List[str] = Field(default_factory=list, description="所有H1标签内容")
    h2_tags: List[str] = Field(default_factory=list, description="所有H2标签内容")
    images: List[Dict[str, str]] = Field(default_factory=list, description="图片列表，格式：[{'src': '...', 'alt': '...'}]")
    links: List[Dict[str, str]] = Field(default_factory=list, description="链接列表，格式：[{'href': '...', 'text': '...'}]")
    word_count: int = Field(default=0, description="正文字数")
