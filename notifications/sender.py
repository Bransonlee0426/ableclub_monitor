import requests
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from core.config import settings
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSender:
    """
    統一的通知發送器，支援 Email 和 Telegram 兩種通知管道
    """
    
    def __init__(self):
        self.supported_channels = [
            "email", 
            "telegram"
        ]
    
    def send_notification(self, message: str, channel: str = "email", **kwargs) -> Dict[str, Any]:
        """
        發送通知到指定管道
        
        Args:
            message (str): 要發送的訊息
            channel (str): 通知管道 (email, telegram)
            **kwargs: 各管道特定參數
        
        Returns:
            dict: 發送結果
        """
        if channel not in self.supported_channels:
            return {"error": f"不支援的通知管道: {channel}"}
        
        try:
            if channel == "email":
                return self._send_email(message, **kwargs)
            elif channel == "telegram":
                return self._send_telegram(message, **kwargs)
            else:
                return {"error": f"未處理的通知管道: {channel}"}
                
        except Exception as e:
            logger.error(f"發送 {channel} 通知時發生錯誤: {e}")
            return {"error": f"發送失敗: {str(e)}"}
    
    def _send_email(self, message: str, subject: str = "AbleClub Monitor 通知", **kwargs) -> Dict[str, Any]:
        """
        發送 Email 通知
        支援實際發送和模擬模式
        """
        try:
            # Get email settings from environment or kwargs - FORCE NEW SETTINGS
            email_user = kwargs.get('email_user') or "anythingemailforgood@gmail.com"
            email_password = kwargs.get('email_password') or "rukmfywwollcoyfx"
            to_email = kwargs.get('to_email') or "xebiva9350@axcradio.com"
            debug_mode = kwargs.get('debug_mode', False)
            
            if not to_email:
                return {"error": "接收 Email 地址未設定"}
            
            # 驗證收件者 Email 格式
            if to_email != "(未設定)" and '@' not in to_email:
                return {"error": f"無效的收件者 Email 格式: {to_email}"}
            
            # 模擬模式：只輸出到 console，不實際發送
            if debug_mode or not email_user or not email_password:
                logger.info("=" * 60)
                logger.info("📧 Email 通知 (模擬模式)")
                logger.info("=" * 60)
                logger.info(f"寄件者: {email_user or '(未設定)'}")
                logger.info(f"收件者: {to_email}")
                logger.info(f"主旨: {subject}")
                logger.info("-" * 60)
                logger.info("內容:")
                logger.info(message)
                logger.info("=" * 60)
                
                return {
                    "message": "Email 通知發送成功 (模擬模式)",
                    "mode": "debug",
                    "from": email_user or "(未設定)",
                    "to": to_email,
                    "subject": subject
                }
            
            # 實際發送模式
            # 驗證 Email 格式並決定 SMTP 伺服器
            if '@' not in email_user:
                return {"error": f"無效的 Email 格式: {email_user}"}
            
            try:
                domain = email_user.split('@')[1].lower()
            except IndexError:
                return {"error": f"無效的 Email 格式: {email_user}"}
            
            # Determine SMTP server based on email domain
            if 'gmail.com' in domain:
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
            elif 'advantech.com' in domain:
                smtp_server = "mail.advantech.com"
                smtp_port = 587
            elif 'outlook.com' in domain or 'hotmail.com' in domain:
                smtp_server = "smtp-mail.outlook.com"
                smtp_port = 587
            else:
                smtp_server = kwargs.get('smtp_server', "smtp.gmail.com")
                smtp_port = kwargs.get('smtp_port', 587)
            
            logger.info(f"嘗試連接 SMTP 伺服器: {smtp_server}:{smtp_port}")
            logger.info(f"使用帳戶: {email_user}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # SMTP configuration
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(email_user, to_email, text)
            server.quit()
            
            logger.info(f"Email 發送成功: {email_user} -> {to_email}")
            return {
                "message": "Email 發送成功",
                "mode": "production",
                "from": email_user,
                "to": to_email,
                "subject": subject,
                "smtp_server": f"{smtp_server}:{smtp_port}"
            }
            
        except Exception as e:
            error_msg = f"Email 發送失敗: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _send_telegram(self, message: str, **kwargs) -> Dict[str, Any]:
        """發送 Telegram 通知"""
        bot_token = kwargs.get('bot_token', settings.TELEGRAM_BOT_TOKEN)
        chat_id = kwargs.get('chat_id', settings.TELEGRAM_CHAT_ID)
        
        if not all([bot_token, chat_id]):
            return {"error": "Telegram 設定不完整"}
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            logger.info("Telegram 通知發送成功")
            return {"status": "success", "message": "Telegram 通知發送成功"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram 通知發送失敗: {e}")
            return {"error": f"Telegram 發送失敗: {str(e)}"}


def test_email_notification():
    """測試 Email 通知功能"""
    sender = NotificationSender()
    test_message = "這是一個測試通知訊息 - Email POC"
    
    result = sender.send_notification(
        message=test_message,
        channel="email",
        subject="AbleClub Monitor - 測試通知"
    )
    
    if result.get("error"):
        logger.error(f"Email 測試失敗: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])
    
    logger.info("Email 測試通知發送成功")
    return result
