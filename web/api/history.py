# 历史记录API路由
from fastapi import APIRouter, HTTPException, Depends, Query

from web.services.history_service import HistoryService
from web.models.responses import HistoryListResponse, ErrorResponse


router = APIRouter(prefix="/api/v1", tags=["history"])


def get_history_service():
    return HistoryService()


@router.get("/history", response_model=HistoryListResponse)
async def get_history_list(
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    severity: str = Query("all", description="筛选严重程度（all/error/warning）"),
    history_service: HistoryService = Depends(get_history_service),
):
    """
    获取历史记录列表

    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **severity**: 筛选条件（all/error/warning）
    """
    try:
        result = history_service.get_history_list(page, page_size, severity)
        return HistoryListResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="HISTORY_LOAD_FAILED",
                message="历史记录加载失败",
                suggestion="请稍后重试",
                details=str(e)
            ).model_dump()
        )


@router.get("/history/{record_id}")
async def get_history_detail(
    record_id: str,
    history_service: HistoryService = Depends(get_history_service),
):
    """
    获取单个历史记录详情

    - **record_id**: 记录ID
    """
    try:
        record = history_service.get_report(record_id)
        return {"report": record["report"]}

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error_code="RECORD_NOT_FOUND",
                message="历史记录不存在",
                suggestion="请检查记录ID是否正确",
                details=str(e)
            ).model_dump()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code="HISTORY_LOAD_FAILED",
                message="历史记录加载失败",
                suggestion="请稍后重试",
                details=str(e)
            ).model_dump()
        )
