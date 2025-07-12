from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

# Create a main router for the v1 API
api_router = APIRouter()

# Include the auth router
# All routes from auth.py will be prefixed with /auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the users router
# All routes from users.py will be prefixed with /users
api_router.include_router(users.router, prefix="/users", tags=["users"])
