from httpx import AsyncClient


async def test_root_endpoint(async_client: AsyncClient):
    """
    Tests the root endpoint ("/") of the application.

    It sends a GET request to the root and verifies that:
    1. The HTTP status code is 200 (OK).
    2. The response JSON matches the expected welcome message.
    """
    # When: a GET request is made to the root endpoint
    response = await async_client.get("/")

    # Then: the response should be successful and contain the welcome message
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Welcome to the AbleClub Monitor API!",
    }
