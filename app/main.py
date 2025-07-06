from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI(
    title="AbleClub Monitor API",
    description="API for serving data scraped from AbleClub.",
    version="0.1.0"
)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check API status.
    """
    return {"status": "ok", "message": "Welcome to the AbleClub Monitor API!"}

# Other endpoints for events, etc., will be added here.
