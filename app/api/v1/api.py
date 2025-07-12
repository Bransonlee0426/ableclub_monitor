from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, notifications

# Create a main router for the v1 API
api_router = APIRouter()

# Include the auth router
# All routes from auth.py will be prefixed with /auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include the users router
# All routes from users.py will be prefixed with /users
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Include the notifications router
# All routes from notifications.py will be prefixed with /notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
