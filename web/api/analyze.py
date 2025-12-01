# 分析API路由
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from web.services.file_service import FileService
from web.services.analyzer_service import AnalyzerService
from web.services.history_service import HistoryService
from web.models.responses import AnalyzeResponse, ErrorResponse, BatchAnalyzeResponse, BatchAnalyzeItem
from md_audit.models.data_models import DiagnosticItem, SeverityLevel, SEOReport
from md_audit.reporter import MarkdownReporter


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/v1", tags=["analyze"])
limiter = Limiter(key_func=get_remote_address)


# 依赖注入（单例服务）
def get_file_service():
    return FileService()


def get_analyzer_service():
    return AnalyzerService()


def get_history_service():
    return HistoryService()


class ExportReportRequest(BaseModel):
    """导出Markdown报告的请求体"""

    file_path: str
    total_score: float
    metadata_score: float
    structure_score: float
    keyword_score: float
    ai_score: float
    intent_score: float = 0
    content_depth_score: float = 0
    eeat_score: float = 0
    ai_search_score: float = 0
    diagnostics: List[dict] = Field(default_factory=list)
    ai_analysis: Optional[dict] = None
    extracted_keywords: List[str] = Field(default_factory=list)
    user_keywords: List[str] = Field(default_factory=list)
    relevance_score: float = 0


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")  # 上传限流（放宽到10次/分钟，便于开发测试）
async def analyze_file(
    request: Request,  # slowapi需要request参数
    file: UploadFile = File(..., description="Markdown文件"),
    file_service: FileService = Depends(get_file_service),
    analyzer_service: AnalyzerService = Depends(get_analyzer_service),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    单文件诊断API

    - **file**: 上传的Markdown文件（<10MB，.md/.txt/.markdown）
    - **keywords**: 用户关键词（可选，Query参数或JSON body）
    """
    try:
        # 1. 保存上传文件
        temp_file = await file_service.save_upload(file)

        # 2. 执行分析（复用现有analyzer）
        report = analyzer_service.analyze_file(str(temp_file))

        # 3. 保存历史记录
        report_dict = report.model_dump()  # Pydantic序列化
        history_id = history_service.save_report(report_dict, file.filename)

        # 4. 清理临时文件
        temp_file.unlink()

        return AnalyzeResponse(report=report_dict, history_id=history_id)

    except ValueError as e:
        # 文件校验错误
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error_code="INVALID_INPUT",
                message=str(e),
                suggestion="请检查文件格式和大小"
            ).model_dump()
        )

    except Exception as e:
        # 分析失败
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="ANALYSIS_FAILED",
                message="诊断失败，请稍后重试",
                suggestion="如果问题持续，请联系管理员",
                details=str(e)
            ).model_dump()
        )


@router.post("/analyze/batch", response_model=BatchAnalyzeResponse)
@limiter.limit("5/minute")  # 批量分析限流更严格
async def analyze_batch(
    request: Request,
    files: List[UploadFile] = File(..., description="多个Markdown文件"),
    file_service: FileService = Depends(get_file_service),
    analyzer_service: AnalyzerService = Depends(get_analyzer_service),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    批量文件诊断API

    - **files**: 多个上传的Markdown文件（每个<10MB，.md/.txt/.markdown）
    - 最多支持50个文件同时上传
    """
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error_code="TOO_MANY_FILES",
                message="文件数量超过限制",
                suggestion="每次最多上传50个文件"
            ).model_dump()
        )

    results = []
    success_count = 0
    failed_count = 0
    total_score = 0.0

    for file in files:
        try:
            # 1. 保存上传文件
            temp_file = await file_service.save_upload(file)

            # 2. 执行分析
            report = analyzer_service.analyze_file(str(temp_file))
            report_dict = report.model_dump()

            # 3. 保存历史记录
            history_id = history_service.save_report(report_dict, file.filename)

            # 4. 清理临时文件
            temp_file.unlink()

            # 5. 记录结果
            results.append(BatchAnalyzeItem(
                file_name=file.filename,
                total_score=report.total_score,
                rules_score=report.rules_score,
                ai_score=report.ai_score,
                history_id=history_id,
                success=True
            ))
            success_count += 1
            total_score += report.total_score

        except Exception as e:
            results.append(BatchAnalyzeItem(
                file_name=file.filename,
                total_score=0,
                rules_score=0,
                ai_score=0,
                history_id="",
                success=False,
                error=str(e)
            ))
            failed_count += 1

    # 计算平均分
    average_score = total_score / success_count if success_count > 0 else 0

    return BatchAnalyzeResponse(
        total_files=len(files),
        success_count=success_count,
        failed_count=failed_count,
        results=results,
        average_score=round(average_score, 1)
    )


@router.post("/analyze/export/markdown", response_class=Response)
async def export_markdown_report(request: ExportReportRequest):
    """根据已有分析结果导出Markdown报告"""
    try:
        # 将诊断列表转换为模型，保持严重程度枚举
        diagnostics = []
        for item in request.diagnostics:
            try:
                severity = SeverityLevel(item.get("severity", "info"))
            except ValueError:
                severity = SeverityLevel.INFO

            diagnostics.append(DiagnosticItem(
                check_name=item.get("check_name", ""),
                category=item.get("category", ""),
                severity=severity,
                score=item.get("score", 0),
                message=item.get("message", ""),
                suggestion=item.get("suggestion", ""),
                current_value=item.get("current_value"),
                expected_value=item.get("expected_value")
            ))

        # 重建 SEOReport 对象
        report = SEOReport(
            file_path=request.file_path,
            total_score=request.total_score,
            metadata_score=request.metadata_score,
            structure_score=request.structure_score,
            keyword_score=request.keyword_score,
            ai_score=request.ai_score,
            intent_score=request.intent_score,
            content_depth_score=request.content_depth_score,
            eeat_score=request.eeat_score,
            ai_search_score=request.ai_search_score,
            relevance_score=request.relevance_score,
            diagnostics=diagnostics,
            ai_analysis=request.ai_analysis,
            extracted_keywords=request.extracted_keywords,
            user_keywords=request.user_keywords
        )

        reporter = MarkdownReporter()
        markdown_content = reporter.generate(report)

        # 生成下载文件名，兼容缺省路径
        filename = f"{Path(request.file_path).stem or 'report'}_seo_report.md"

        return Response(
            content=markdown_content,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except Exception as exc:  # pragma: no cover - 防御性兜底
        logger.error("Export markdown failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="EXPORT_FAILED",
                message="导出报告失败",
                suggestion="请稍后重试",
                details=str(exc)
            ).model_dump()
        )
