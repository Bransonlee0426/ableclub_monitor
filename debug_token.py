#!/usr/bin/env python3
"""
Debug utility to generate a long-lived test token for development.
Usage: python debug_token.py
"""

from core.security import create_access_token
from datetime import timedelta

def generate_debug_token(username: str = "bransonlee0426@gmail.com", days: int = 30):
    """Generate a long-lived token for development testing"""
    # Create token that expires in 30 days
    expires_delta = timedelta(days=days)
    token = create_access_token(subject=username, expires_delta=expires_delta)
    
    print(f"🔧 Debug Token for: {username}")
    print(f"⏰ Expires in: {days} days")
    print(f"🎫 Token:")
    print(token)
    print("\n📋 Copy this for Swagger Authorization:")
    print(f"Bearer {token}")
    print("\n🔗 Or use in curl:")
    print(f"curl -H 'Authorization: Bearer {token}' http://127.0.0.1:8000/api/v1/me/notify-settings/")
    
    return token

if __name__ == "__main__":
    generate_debug_token()