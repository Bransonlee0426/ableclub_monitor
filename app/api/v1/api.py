from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, notifications, admin, notify_settings, dev_auth, keywords

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

# Include the admin router
# All routes from admin.py will be prefixed with /admin
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Include the notify settings router
# All routes from notify_settings.py will be prefixed with /me/notify-settings
api_router.include_router(notify_settings.router, prefix="/me/notify-settings", tags=["Notify Settings"])

# Include the keywords router
# All routes from keywords.py will be prefixed with /me/keywords
api_router.include_router(keywords.router, prefix="/me/keywords", tags=["Keywords"])

# Include development auth router (only in development)
# All routes from dev_auth.py will be prefixed with /dev
api_router.include_router(dev_auth.router, prefix="/dev", tags=["🚧 Development Only"])
