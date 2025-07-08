# /notifications/line_auth_router.py

import requests
from fastapi import APIRouter, Request, HTTPException, status
from starlette.responses import RedirectResponse
from typing import Optional

from core.config import settings

# Create a new router for LINE authentication endpoints.
router = APIRouter()

# This is a placeholder for the actual database interaction function.
# In a real application, this would save the token to the user's record in the database.
def save_token_to_db(user_id: int, token: str):
    """
    Placeholder function to simulate saving the access token to the database.
    """
    # In a real implementation, you would have database logic here.
    # For example:
    # with get_db() as db:
    #     user = db.query(User).filter(User.id == user_id).first()
    #     if user:
    #         user.line_notify_token = token
    #         db.commit()
    print(f"Simulating save: User ID '{user_id}' received token: '{token}'")


@router.get("/api/line/callback", tags=["LINE Authentication"])

def line_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    """
    Handles the OAuth 2.0 callback from LINE Notify.

    This endpoint receives the authorization code from LINE, exchanges it for an
    access token, and stores the token for the user.
    """
    # The 'state' parameter should contain the user_id to identify who is authorizing.
    user_id = state

    # 1. Validate that 'code' and 'state' (user_id) are present.
    if not code or not user_id:
        print("Error: Missing 'code' or 'state' (user_id) in callback.")
        return RedirectResponse(url=settings.FRONTEND_REDIRECT_FAILURE_URL)

    # 2. Prepare the request to exchange the code for an access token.
    token_url = "https://notify-api.line.me/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINE_REDIRECT_URI,
        "client_id": settings.LINE_CLIENT_ID,
        "client_secret": settings.LINE_CLIENT_SECRET,
    }

    try:
        # 3. Send the POST request to LINE's token endpoint.
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx).

        # 4. Parse the access token from the response.
        response_data = response.json()
        access_token = response_data.get("access_token")

        if not access_token:
            print(f"Error: 'access_token' not found in LINE's response. Response: {response_data}")
            return RedirectResponse(url=settings.FRONTEND_REDIRECT_FAILURE_URL)

        # 5. Save the access token to the database (using the placeholder function).
        # The user_id is retrieved from the 'state' parameter.
        save_token_to_db(user_id=int(user_id), token=access_token)

        # 6. Redirect the user to the success page.
        return RedirectResponse(url=settings.FRONTEND_REDIRECT_SUCCESS_URL)

    except requests.exceptions.RequestException as e:
        # Handle network errors or bad responses from LINE.
        print(f"Error during request to LINE token endpoint: {e}")
        return RedirectResponse(url=settings.FRONTEND_REDIRECT_FAILURE_URL)
    except (KeyError, ValueError) as e:
        # Handle errors in parsing the response.
        print(f"Error parsing LINE's response: {e}")
        return RedirectResponse(url=settings.FRONTEND_REDIRECT_FAILURE_URL)