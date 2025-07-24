from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from schemas.auth import ResponseModel
from schemas.scraped_event import ScrapedEvent as ScrapedEventSchema
from database.session import get_db
from crud import crud_scraped_event

router = APIRouter()


@router.get("/", 
            response_model=ResponseModel,
            tags=["Scraped Events"], 
            summary="取得已爬取的活動列表",
            description="分頁查詢所有已爬取並儲存的活動資料")
async def get_scraped_events(
    skip: int = Query(default=0, ge=0, description="跳過的記錄數量（用於分頁）"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁返回的最大記錄數量"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all scraped events.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        db: Database session
        
    Returns:
        ResponseModel: Contains list of scraped events with pagination info
    """
    try:
        events = crud_scraped_event.get_events(db=db, skip=skip, limit=limit)
        
        # Convert to response format
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "start_date": event.start_date.isoformat(),
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "is_processed": event.is_processed,
                "created_at": event.created_at.isoformat()
            })
        
        return ResponseModel(
            success=True,
            message=f"成功取得 {len(events_data)} 筆活動資料",
            data={
                "events": events_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "returned_count": len(events_data)
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得活動列表失敗: {str(e)}"
        )


@router.get("/unprocessed", 
            response_model=ResponseModel,
            tags=["Scraped Events"], 
            summary="取得未處理的活動列表",
            description="分頁查詢所有未處理（is_processed=False）的活動資料")
async def get_unprocessed_events(
    skip: int = Query(default=0, ge=0, description="跳過的記錄數量（用於分頁）"),
    limit: int = Query(default=20, ge=1, le=100, description="每頁返回的最大記錄數量"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of unprocessed scraped events.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return (1-100)
        db: Database session
        
    Returns:
        ResponseModel: Contains list of unprocessed events with pagination info
    """
    try:
        events = crud_scraped_event.get_unprocessed_events(db=db, skip=skip, limit=limit)
        
        # Convert to response format
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "title": event.title,
                "start_date": event.start_date.isoformat(),
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "is_processed": event.is_processed,
                "created_at": event.created_at.isoformat()
            })
        
        return ResponseModel(
            success=True,
            message=f"成功取得 {len(events_data)} 筆未處理活動",
            data={
                "events": events_data,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "returned_count": len(events_data)
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得未處理活動列表失敗: {str(e)}"
        )


@router.get("/{event_id}", 
            response_model=ResponseModel,
            tags=["Scraped Events"], 
            summary="根據 ID 取得特定活動",
            description="根據活動 ID 查詢單一已爬取的活動詳細資料")
async def get_scraped_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scraped event by its ID.
    
    Args:
        event_id: ID of the event to retrieve
        db: Database session
        
    Returns:
        ResponseModel: Contains the requested event data
    """
    try:
        event = crud_scraped_event.get_event_by_id(db=db, event_id=event_id)
        
        if not event:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 ID 為 {event_id} 的活動"
            )
        
        event_data = {
            "id": event.id,
            "title": event.title,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "is_processed": event.is_processed,
            "created_at": event.created_at.isoformat()
        }
        
        return ResponseModel(
            success=True,
            message="成功取得活動資料",
            data={"event": event_data}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得活動資料失敗: {str(e)}"
        )




@router.delete("/{event_id}", 
               response_model=ResponseModel,
               tags=["Scraped Events"], 
               summary="刪除指定活動",
               description="根據活動 ID 永久刪除已爬取的活動資料")
async def delete_scraped_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a scraped event by its ID.
    
    Args:
        event_id: ID of the event to delete
        db: Database session
        
    Returns:
        ResponseModel: Confirmation of deletion
    """
    try:
        # First check if event exists
        existing_event = crud_scraped_event.get_event_by_id(db=db, event_id=event_id)
        
        if not existing_event:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 ID 為 {event_id} 的活動"
            )
        
        # Store event info before deletion for response
        event_info = {
            "id": existing_event.id,
            "title": existing_event.title,
            "start_date": existing_event.start_date.isoformat()
        }
        
        # Delete the event
        deleted = crud_scraped_event.delete_event(db=db, event_id=event_id)
        
        if not deleted:
            raise HTTPException(
                status_code=500,
                detail="刪除活動時發生未知錯誤"
            )
        
        return ResponseModel(
            success=True,
            message=f"活動 ID {event_id} 已成功刪除",
            data={"deleted_event": event_info}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除活動失敗: {str(e)}"
        )


@router.put("/{event_id}/processed", 
            response_model=ResponseModel,
            tags=["Scraped Events"], 
            summary="標記活動為已處理",
            description="將指定的活動標記為已處理狀態（is_processed=True）")
async def mark_event_as_processed(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a scraped event as processed.
    
    Args:
        event_id: ID of the event to mark as processed
        db: Database session
        
    Returns:
        ResponseModel: Confirmation of status update
    """
    try:
        # Update the event's processed status
        updated_event = crud_scraped_event.update_processed_status(
            db=db, 
            event_id=event_id, 
            is_processed=True
        )
        
        if not updated_event:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 ID 為 {event_id} 的活動"
            )
        
        event_data = {
            "id": updated_event.id,
            "title": updated_event.title,
            "start_date": updated_event.start_date.isoformat(),
            "end_date": updated_event.end_date.isoformat() if updated_event.end_date else None,
            "is_processed": updated_event.is_processed,
            "created_at": updated_event.created_at.isoformat()
        }
        
        return ResponseModel(
            success=True,
            message=f"活動 ID {event_id} 已標記為已處理",
            data={"event": event_data}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新活動狀態失敗: {str(e)}"
        )


@router.get("/stats/summary", 
            response_model=ResponseModel,
            tags=["Scraped Events"], 
            summary="活動統計摘要",
            description="取得已爬取活動的統計資訊，包括總數、已處理數、未處理數等")
async def get_events_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics of scraped events.
    
    Args:
        db: Database session
        
    Returns:
        ResponseModel: Contains event statistics
    """
    try:
        # Get all events for counting
        all_events = crud_scraped_event.get_events(db=db, skip=0, limit=1000)  # Reasonable limit for counting
        processed_events = [e for e in all_events if e.is_processed]
        unprocessed_events = [e for e in all_events if not e.is_processed]
        
        stats = {
            "total_events": len(all_events),
            "processed_events": len(processed_events),
            "unprocessed_events": len(unprocessed_events),
            "processed_percentage": round((len(processed_events) / len(all_events)) * 100, 2) if all_events else 0
        }
        
        return ResponseModel(
            success=True,
            message="成功取得活動統計資訊",
            data={"statistics": stats}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取得統計資訊失敗: {str(e)}"
        )