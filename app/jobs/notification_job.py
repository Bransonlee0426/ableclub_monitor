import httpx
import logging
import os
from typing import Dict, List, Set, Any, Optional
from notifications.sender import NotificationSender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get base API URL from environment or use localhost for development
BASE_API_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:8000")


def process_and_notify_users():
    """
    比對與通知核心函式：獲取所有使用者設定和新活動，進行關鍵字比對，
    並為匹配成功的使用者聚合並發送一封摘要式的 Email 通知，
    最後更新已處理活動的狀態。
    
    Functions:
    1. Get all user notification settings via API
    2. Get all unprocessed events via API  
    3. Match keywords with event titles (case-insensitive)
    4. Aggregate notifications for each user
    5. Send email notifications to matched users
    6. Update processed event status via API
    """
    logger.info("開始執行通知處理任務...")
    
    # Initialize notification sender
    notification_sender = NotificationSender()
    
    try:
        # Sub-task 2.1: Get data via HTTP API
        all_user_settings = _get_all_user_settings()
        if not all_user_settings:
            logger.info("沒有使用者設定資料，任務結束")
            return
            
        unprocessed_events = _get_unprocessed_events()
        if not unprocessed_events:
            logger.info("沒有未處理的活動，任務結束")
            return
            
        logger.info(f"獲取到 {len(all_user_settings)} 個使用者設定")
        logger.info(f"獲取到 {len(unprocessed_events)} 個未處理活動")
        
        # Sub-task 2.2: Match keywords and aggregate notifications
        notifications_to_send = {}  # {email: [event_titles]}
        processed_event_ids: Set[int] = set()
        
        # Nested loop for keyword matching
        for user_setting in all_user_settings:
            user_email = user_setting.get("email_address")
            user_keywords = user_setting.get("keywords", [])
            is_active = user_setting.get("is_active", False)
            
            # Skip inactive users or users without email
            if not is_active or not user_email:
                continue
                
            matched_events = []
            
            for event in unprocessed_events:
                event_title = event.get("title", "")
                event_id = event.get("id")
                
                # Case-insensitive keyword matching
                for keyword in user_keywords:
                    if keyword.lower() in event_title.lower():
                        matched_events.append(event_title)
                        processed_event_ids.add(event_id)
                        break  # Avoid duplicate matches for the same event
            
            # Aggregate notifications for this user
            if matched_events:
                notifications_to_send[user_email] = matched_events
        
        logger.info(f"需要發送通知給 {len(notifications_to_send)} 個使用者")
        logger.info(f"總共匹配到 {len(processed_event_ids)} 個活動")
        
        # Sub-task 2.3: Send notifications
        _send_email_notifications(notifications_to_send, notification_sender)
        
        # Sub-task 2.4: Update event status
        _update_processed_events(processed_event_ids)
        
        logger.info("通知處理任務完成")
        
    except Exception as e:
        logger.error(f"通知處理任務執行失敗: {str(e)}")
        raise


def _get_all_user_settings() -> List[Dict[str, Any]]:
    """
    Get all user notification settings via API call.
    
    Returns:
        List of user notification settings with keywords
    """
    try:
        # Get authentication token (for demo purposes, using a simple approach)
        # In production, this should use proper service-to-service authentication
        auth_token = _get_auth_token()
        if not auth_token:
            logger.error("無法獲取認證 token")
            return []
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_API_URL}/api/v1/admin/notify-settings",
                headers=headers,
                params={"limit": 1000}  # Get all settings
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success") and data.get("data", {}).get("items"):
                return data["data"]["items"]
            else:
                logger.warning("API 回應格式異常或無資料")
                return []
                
    except httpx.RequestError as e:
        logger.error(f"獲取使用者設定時發生網路錯誤: {str(e)}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"獲取使用者設定 API 回應錯誤: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"獲取使用者設定時發生未知錯誤: {str(e)}")
        return []


def _get_unprocessed_events() -> List[Dict[str, Any]]:
    """
    Get all unprocessed events via API call.
    
    Returns:
        List of unprocessed events
    """
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_API_URL}/api/v1/scraped-events/unprocessed",
                params={"limit": 100}  # Get unprocessed events (max allowed: 100)
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success") and data.get("data", {}).get("events"):
                return data["data"]["events"]
            else:
                logger.warning("未處理活動 API 回應格式異常或無資料")
                return []
                
    except httpx.RequestError as e:
        logger.error(f"獲取未處理活動時發生網路錯誤: {str(e)}")
        return []
    except httpx.HTTPStatusError as e:
        logger.error(f"獲取未處理活動 API 回應錯誤: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"獲取未處理活動時發生未知錯誤: {str(e)}")
        return []


def _send_email_notifications(notifications_to_send: Dict[str, List[str]], 
                            notification_sender: NotificationSender) -> None:
    """
    Send email notifications to users with matched events.
    
    Args:
        notifications_to_send: Dictionary mapping email to list of event titles
        notification_sender: NotificationSender instance
    """
    for email, event_titles in notifications_to_send.items():
        try:
            # Format email content
            content = _format_email_content(event_titles)
            
            # Send email notification
            result = notification_sender.send_notification(
                message=content,
                channel="email",
                to_email=email,
                subject="您關注的 AbleClub 活動有新消息！"
            )
            
            if result.get("error"):
                logger.error(f"發送郵件給 {email} 失敗: {result['error']}")
            else:
                logger.info(f"成功發送郵件給 {email}，包含 {len(event_titles)} 個活動")
                
        except Exception as e:
            logger.error(f"發送郵件給 {email} 時發生異常: {str(e)}")
            # Continue with other users even if one fails


def _update_processed_events(processed_event_ids: Set[int]) -> None:
    """
    Update event status to processed via API calls.
    
    Args:
        processed_event_ids: Set of event IDs to mark as processed
    """
    # Get authentication token
    auth_token = _get_auth_token()
    if not auth_token:
        logger.error("無法獲取認證 token，跳過狀態更新")
        return
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for event_id in processed_event_ids:
        try:
            with httpx.Client() as client:
                response = client.put(
                    f"{BASE_API_URL}/api/v1/scraped-events/{event_id}/processed",
                    headers=headers
                )
                response.raise_for_status()
                
                logger.info(f"成功更新活動 {event_id} 為已處理狀態")
                
        except httpx.RequestError as e:
            logger.error(f"更新活動 {event_id} 狀態時發生網路錯誤: {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"更新活動 {event_id} 狀態 API 回應錯誤: {e.response.status_code}")
        except Exception as e:
            logger.error(f"更新活動 {event_id} 狀態時發生異常: {str(e)}")
            # Continue with other events even if one fails


def _format_email_content(event_titles: List[str]) -> str:
    """
    Format email content with event titles in a readable format.
    
    Args:
        event_titles: List of event titles to include in email
        
    Returns:
        Formatted email content string
    """
    content = "親愛的用戶您好，\n\n"
    content += "以下是您關注的關鍵字匹配到的最新 AbleClub 活動：\n\n"
    
    for i, title in enumerate(event_titles, 1):
        content += f"{i}. {title}\n"
    
    content += "\n" + "="*50 + "\n"
    content += "請登入 AbleClub 官網查看詳細資訊。\n\n"
    content += "此郵件由 AbleClub Monitor 系統自動發送，請勿回覆。\n"
    content += "如需取消訂閱，請聯繫系統管理員。"
    
    return content


def _get_auth_token() -> Optional[str]:
    """
    Get authentication token for API calls.
    For demo purposes, this returns a fixed token.
    In production, this should implement proper service-to-service authentication.
    
    Returns:
        Authentication token string or None if failed
    """
    try:
        # For demo, using dev login to get token
        # In production, this should use service account or other secure methods
        with httpx.Client() as client:
            response = client.post(
                f"{BASE_API_URL}/api/v1/dev/dev-login",
                json={"username": "admin"}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success") and data.get("data", {}).get("access_token"):
                return data["data"]["access_token"]
            else:
                logger.error("登入 API 回應格式異常")
                return None
                
    except Exception as e:
        logger.error(f"獲取認證 token 失敗: {str(e)}")
        return None


if __name__ == "__main__":
    """Test the notification job function"""
    process_and_notify_users()