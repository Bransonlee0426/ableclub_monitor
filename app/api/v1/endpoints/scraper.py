from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from schemas.auth import ResponseModel
from schemas.scraped_event import ScrapedEventCreate
from scraper.tasks import scrape_main_menu, scrape_corporate_events
from playwright.async_api import async_playwright
from database.session import get_db
from crud import crud_scraped_event

router = APIRouter()


@router.get("/main-menu", 
            response_model=ResponseModel,
            tags=["Scraper"], 
            summary="爬取主選單項目",
            description="僅爬取 AbleClub 首頁的主選單項目")
async def get_main_menu():
    """
    Scrape only the main menu items from AbleClub homepage.
    
    Returns:
        ResponseModel: Contains main menu items list
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to AbleClub homepage
                await page.goto("https://ableclub.advantech.com.tw/Taiwan/zh-tw", 
                              wait_until="domcontentloaded")
                
                # Scrape main menu
                menu_items = await scrape_main_menu(page)
                
                return ResponseModel(
                    success=True,
                    message="主選單爬取成功",
                    data={"menu_items": menu_items}
                )
                
            finally:
                await browser.close()
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"主選單爬取失敗: {str(e)}"
        )

@router.get("/corporate-events", 
            response_model=ResponseModel,
            tags=["Scraper"], 
            summary="爬取公司活動",
            description="爬取 AbleClub 公司活動頁面中「報名中活動」的所有活動標題並儲存到資料庫")
async def get_corporate_events(db: Session = Depends(get_db)):
    """
    Scrape corporate events that are open for registration.
    
    Returns:
        ResponseModel: Contains list of event titles
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to AbleClub homepage
                await page.goto("https://ableclub.advantech.com.tw/Taiwan/zh-tw", 
                              wait_until="domcontentloaded")
                
                # First check if corporate events menu exists
                menu_items = await scrape_main_menu(page)
                
                if "公司活動" not in menu_items:
                    return ResponseModel(
                        success=False,
                        message="主選單中未找到「公司活動」選項",
                        data={"events": []}
                    )
                
                # Navigate to corporate events page
                await page.get_by_text("公司活動", exact=True).click()
                await page.wait_for_url("**/Event?categoryId=**")
                
                # Scrape corporate events
                event_data = await scrape_corporate_events(page)
                
                # Save scraped events to database
                saved_count = 0
                new_events = []
                
                for event in event_data:
                    try:
                        # Convert string dates to date objects
                        start_date = None
                        end_date = None
                        
                        if event.get('start_date'):
                            try:
                                start_date = datetime.strptime(event['start_date'], '%Y/%m/%d').date()
                            except ValueError:
                                print(f"無法解析開始日期: {event['start_date']}")
                                continue
                        
                        if event.get('end_date'):
                            try:
                                end_date = datetime.strptime(event['end_date'], '%Y/%m/%d').date()
                            except ValueError:
                                print(f"無法解析結束日期: {event['end_date']}")
                                # Continue anyway, end_date is optional
                        
                        # Skip if no valid start_date
                        if not start_date:
                            continue
                        
                        # Create ScrapedEventCreate object
                        event_create = ScrapedEventCreate(
                            title=event['title'],
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        # Save to database using create_or_ignore
                        # Check if event already exists before saving
                        existing_event = crud_scraped_event.get_event_by_title_and_date(
                            db=db, title=event['title'], start_date=start_date
                        )
                        
                        saved_event = crud_scraped_event.create_or_ignore(db=db, event_in=event_create)
                        
                        # If no existing event was found, this is a new event
                        if not existing_event:
                            saved_count += 1
                            new_events.append({
                                "id": saved_event.id,
                                "title": saved_event.title,
                                "start_date": saved_event.start_date.isoformat(),
                                "end_date": saved_event.end_date.isoformat() if saved_event.end_date else None,
                                "is_processed": saved_event.is_processed,
                                "created_at": saved_event.created_at.isoformat()
                            })
                        
                    except Exception as e:
                        print(f"儲存活動時發生錯誤: {e}")
                        # Continue with next event
                        continue
                
                return ResponseModel(
                    success=True,
                    message=f"成功爬取 {len(event_data)} 個活動，儲存 {saved_count} 個新活動到資料庫",
                    data={
                        "scraped_events": event_data,
                        "saved_new_events": new_events,
                        "total_scraped": len(event_data),
                        "total_saved_new": saved_count
                    }
                )
                
            finally:
                await browser.close()
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"公司活動爬取失敗: {str(e)}"
        )


@router.get("/status", 
            response_model=ResponseModel,
            tags=["Scraper"], 
            summary="爬蟲模組狀態檢查",
            description="檢查爬蟲模組和相關依賴的狀態")
async def scraper_status():
    """
    Check the status of scraper module and dependencies.
    
    Returns:
        ResponseModel: Status information about scraper module
    """
    try:
        # Check if Playwright is available
        from playwright.async_api import async_playwright
        
        status_info = {
            "playwright_available": True,
            "scraper_module": "available",
            "target_url": "https://ableclub.advantech.com.tw/Taiwan/zh-tw"
        }
        
        return ResponseModel(
            success=True,
            message="爬蟲模組狀態正常",
            data=status_info
        )
        
    except ImportError as e:
        return ResponseModel(
            success=False,
            message="爬蟲模組依賴缺失",
            data={"error": f"Missing dependency: {str(e)}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"狀態檢查失敗: {str(e)}"
        )