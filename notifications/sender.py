from core.config import settings

def send_line_notification(message: str):
    """
    Placeholder for sending a notification via Line Notify.
    """
    if not settings.LINE_NOTIFY_TOKEN:
        print("LINE_NOTIFY_TOKEN not set. Skipping notification.")
        return
    
    print(f"Attempting to send Line notification: {message}")
    # Business logic for calling Line Notify API will be implemented here.
    pass
