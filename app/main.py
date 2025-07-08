from fastapi import FastAPI
# Import the newly created router
from notifications import line_auth_router

# Create FastAPI app instance
app = FastAPI(
    title="AbleClub Monitor API",
    description="API for serving data scraped from AbleClub.",
    version="0.1.0"
)

# Include the LINE authentication router
# All routes defined in line_auth_router will now be part of the application.
app.include_router(line_auth_router.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check API status.
    """
    return {"status": "ok", "message": "Welcome to the AbleClub Monitor API!"}

# Other endpoints for events, etc., will be added here.
