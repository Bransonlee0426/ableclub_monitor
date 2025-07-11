import sys
import os
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

# Add the project root directory to the Python path
# This allows pytest to find the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    A fixture that provides an asynchronous test client for the API.
    This client can be used to make requests to the application in tests.
    The scope is 'function' to ensure a clean client for each test.
    """
    # Use ASGITransport to wrap the FastAPI app
    transport = ASGITransport(app=app)
    
    # Use httpx.AsyncClient with the ASGI transport
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Yield the client to the test function
        yield client
