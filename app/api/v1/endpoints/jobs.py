from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from sqlalchemy.orm import Session

from database.session import get_db
from schemas.auth import ResponseModel
from schemas.job_execution_history import (
    JobExecutionHistoryResponse, 
    JobStatsResponse,
    JobStatusResponse
)
from crud.crud_job_execution_history import crud_job_execution_history
from scheduler.job_manager import get_job_status, stop_job, trigger_corporate_events_job

router = APIRouter()


@router.get("/jobs/scraper/status",
            response_model=ResponseModel,
            tags=["Jobs"],
            summary="查看爬蟲任務狀態",
            description="查看 corporate events 爬蟲任務的當前狀態")
async def get_scraper_job_status():
    """
    Get current status of the corporate events scraper job
    
    Returns:
        ResponseModel: Contains job status, last execution time, and result
    """
    try:
        status_info = await get_job_status()
        
        return ResponseModel(
            success=True,
            message="任務狀態查詢成功",
            data=status_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查詢任務狀態失敗: {str(e)}"
        )


@router.post("/jobs/scraper/stop",
             response_model=ResponseModel,
             tags=["Jobs"],
             summary="停止爬蟲任務",
             description="手動停止 corporate events 爬蟲任務")
async def stop_scraper_job():
    """
    Manually stop the corporate events scraper job
    
    Returns:
        ResponseModel: Result of stop operation
    """
    try:
        result = await stop_job()
        
        return ResponseModel(
            success=True,
            message="任務已停止",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"停止任務失敗: {str(e)}"
        )


@router.get("/jobs/scraper/last-execution",
            response_model=ResponseModel,
            tags=["Jobs"],
            summary="查看最新執行記錄",
            description="查看 corporate events 爬蟲任務的最新一次執行記錄")
async def get_last_execution(db: Session = Depends(get_db)):
    """
    Get the latest execution record for the scraper job
    
    Returns:
        ResponseModel: Latest execution record
    """
    try:
        latest_execution = crud_job_execution_history.get_latest_execution(db)
        
        if not latest_execution:
            return ResponseModel(
                success=True,
                message="尚無執行記錄",
                data=None
            )
        
        return ResponseModel(
            success=True,
            message="最新執行記錄查詢成功",
            data=JobExecutionHistoryResponse.model_validate(latest_execution)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查詢執行記錄失敗: {str(e)}"
        )


@router.get("/jobs/scraper/history",
            response_model=ResponseModel,
            tags=["Jobs"],
            summary="查看執行歷史記錄",
            description="分頁查看 corporate events 爬蟲任務的執行歷史記錄")
async def get_execution_history(
    page: int = Query(1, ge=1, description="頁數"),
    limit: int = Query(10, ge=1, le=100, description="每頁筆數"),
    status: str = Query(None, description="狀態篩選: success, failed, running, paused, resumed"),
    db: Session = Depends(get_db)
):
    """
    Get paginated execution history for the scraper job
    
    Args:
        page: Page number (starts from 1)
        limit: Number of records per page
        status: Filter by status (optional)
        db: Database session
        
    Returns:
        ResponseModel: Paginated execution history records
    """
    try:
        skip = (page - 1) * limit
        
        # Get records with optional status filter
        if status:
            # For filtered results, we need a custom query
            from models.job_execution_history import JobExecutionHistory
            executions = (
                db.query(JobExecutionHistory)
                .filter(JobExecutionHistory.status == status)
                .order_by(JobExecutionHistory.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            executions = crud_job_execution_history.get_by_job_name(
                db=db,
                skip=skip,
                limit=limit
            )
        
        execution_responses = [
            JobExecutionHistoryResponse.model_validate(execution) 
            for execution in executions
        ]
        
        return ResponseModel(
            success=True,
            message=f"執行歷史查詢成功，第 {page} 頁，共 {len(execution_responses)} 筆記錄",
            data={
                "executions": execution_responses,
                "page": page,
                "limit": limit,
                "total_records": len(execution_responses)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查詢執行歷史失敗: {str(e)}"
        )


@router.get("/jobs/scraper/history/{execution_id}",
            response_model=ResponseModel,
            tags=["Jobs"],
            summary="查看特定執行記錄詳情",
            description="查看指定 ID 的執行記錄詳細資訊")
async def get_execution_detail(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific execution record
    
    Args:
        execution_id: ID of the execution record
        db: Database session
        
    Returns:
        ResponseModel: Detailed execution record
    """
    try:
        execution = crud_job_execution_history.get(db, execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 ID 為 {execution_id} 的執行記錄"
            )
        
        return ResponseModel(
            success=True,
            message="執行記錄詳情查詢成功",
            data=JobExecutionHistoryResponse.model_validate(execution)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查詢執行記錄詳情失敗: {str(e)}"
        )


@router.get("/jobs/scraper/stats",
            response_model=ResponseModel,
            tags=["Jobs"],
            summary="查看執行統計",
            description="查看指定天數內的任務執行統計資訊")
async def get_execution_stats(
    days: int = Query(7, ge=1, le=30, description="統計天數"),
    db: Session = Depends(get_db)
):
    """
    Get execution statistics for the last N days
    
    Args:
        days: Number of days to analyze (1-30)
        db: Database session
        
    Returns:
        ResponseModel: Execution statistics
    """
    try:
        stats = crud_job_execution_history.get_execution_stats(db, days=days)
        
        return ResponseModel(
            success=True,
            message=f"最近 {days} 天執行統計查詢成功",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查詢執行統計失敗: {str(e)}"
        )


@router.post("/jobs/scraper/trigger",
             response_model=ResponseModel,
             tags=["Jobs"],
             summary="手動觸發任務",
             description="手動觸發執行一次 corporate events 爬蟲任務（開發用）")
async def trigger_scraper_job():
    """
    Manually trigger the corporate events scraper job
    This endpoint is for development and testing purposes
    
    Returns:
        ResponseModel: Trigger operation result
    """
    try:
        result = await trigger_corporate_events_job()
        
        return ResponseModel(
            success=True,
            message="任務已手動觸發執行",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"手動觸發任務失敗: {str(e)}"
        )


@router.get("/health/scheduler",
            response_model=ResponseModel,
            tags=["Health"],
            summary="排程器健康檢查",
            description="檢查排程器和相關服務的健康狀態")
async def scheduler_health_check():
    """
    Check the health status of the job scheduler
    
    Returns:
        ResponseModel: Scheduler health information
    """
    try:
        from scheduler.job_scheduler import scheduler_manager
        
        health_info = {
            "scheduler_running": scheduler_manager.is_running,
            "job_scheduled": scheduler_manager.is_job_running("corporate_events_scraper"),
            "job_paused": scheduler_manager.is_job_paused("corporate_events_scraper"),
            "next_run_time": scheduler_manager.get_next_run_time("corporate_events_scraper")
        }
        
        return ResponseModel(
            success=True,
            message="排程器健康檢查完成",
            data=health_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"排程器健康檢查失敗: {str(e)}"
        )