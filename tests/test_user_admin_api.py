"""
Test suite for the User Management API endpoints.

This file contains comprehensive tests for the following APIs:
- GET /api/v1/admin/users
- GET /api/v1/admin/users/{id}
- PATCH /api/v1/admin/users/{id}
- DELETE /api/v1/admin/users/{id}

The tests follow Test-Driven Development (TDD) methodology and use pytest with mocking
to test the API logic in isolation.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from datetime import datetime, timezone


# --- Test Data Constants ---

# Mock user objects for testing
MOCK_ACTIVE_USER = MagicMock(
    id=1,
    username="active@example.com",
    invite_code_used="WELCOME2024",
    is_active=True,
    created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
)

MOCK_INACTIVE_USER = MagicMock(
    id=2,
    username="inactive@example.com",
    invite_code_used="WELCOME2024",
    is_active=False,
    created_at=datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    updated_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
)


# --- Tests for GET /api/v1/admin/users ---

@pytest.mark.asyncio
async def test_get_users_success_should_return_200(async_client: AsyncClient, mocker):
    """
    Test successful retrieval of users list.
    """
    # Arrange: Mock the database response
    mock_users = [MOCK_ACTIVE_USER, MOCK_INACTIVE_USER]
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_users", return_value=(mock_users, 2))

    # Act: Send the list request
    response = await async_client.get("/api/v1/admin/users")

    # Assert: Verify the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] == True
    assert response_data["message"] == "查詢成功"
    data = response_data["data"]
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["pages"] == 1
    
    # Verify that password_hash is not included in response
    for user in data["items"]:
        assert "password_hash" not in user


@pytest.mark.asyncio
async def test_get_users_with_active_filter_should_return_200(async_client: AsyncClient, mocker):
    """
    Test retrieval with active status filter.
    """
    # Arrange: Mock filtering for active users only
    mock_users = [MOCK_ACTIVE_USER]
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_users", return_value=(mock_users, 1))

    # Act: Send request with filter
    response = await async_client.get("/api/v1/admin/users?is_active=true")

    # Assert: Verify the filtered response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["is_active"] is True


@pytest.mark.asyncio
async def test_get_users_with_pagination_should_return_200(async_client: AsyncClient, mocker):
    """
    Test retrieval with pagination parameters.
    """
    # Arrange: Mock paginated response
    mock_users = [MOCK_ACTIVE_USER]
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_users", return_value=(mock_users, 10))

    # Act: Send request with pagination
    response = await async_client.get("/api/v1/admin/users?page=2&size=5")

    # Assert: Verify the paginated response
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 5
    assert data["pages"] == 2  # 10 total / 5 size = 2 pages


# --- Tests for GET /api/v1/admin/users/{id} ---

@pytest.mark.asyncio
async def test_get_user_by_id_success_should_return_200(async_client: AsyncClient, mocker):
    """
    Test successful retrieval of a single user.
    """
    # Arrange: Mock the database response
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_user_by_id", return_value=MOCK_ACTIVE_USER)

    # Act: Send the request
    response = await async_client.get("/api/v1/admin/users/1")

    # Assert: Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "active@example.com"
    assert data["is_active"] is True
    # Verify password_hash is not included
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_get_user_by_id_not_found_should_return_404(async_client: AsyncClient, mocker):
    """
    Test retrieval of non-existent user should return 404.
    """
    # Arrange: Mock that the user doesn't exist
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_user_by_id", return_value=None)

    # Act: Send request for non-existent user
    response = await async_client.get("/api/v1/admin/users/999")

    # Assert: Verify not found response
    assert response.status_code == 404
    assert response.json() == {"detail": "使用者不存在"}


# --- Tests for PATCH /api/v1/admin/users/{id} ---

@pytest.mark.asyncio
async def test_update_user_success_should_return_200(async_client: AsyncClient, mocker):
    """
    Test successful update of a user's active status.
    """
    # Arrange: Mock successful update
    updated_mock = MagicMock(
        id=1,
        username="active@example.com",
        invite_code_used="WELCOME2024",
        is_active=False,  # Changed to inactive
        created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    )
    mocker.patch("app.api.v1.endpoints.admin.crud_user.update_user_active_status", return_value=updated_mock)

    # Act: Send the update request
    response = await async_client.patch(
        "/api/v1/admin/users/1",
        json={
            "is_active": False
        }
    )

    # Assert: Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["is_active"] is False
    # Verify password_hash is not included
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_update_user_not_found_should_return_404(async_client: AsyncClient, mocker):
    """
    Test update of non-existent user should return 404.
    """
    # Arrange: Mock that the user doesn't exist
    mocker.patch("app.api.v1.endpoints.admin.crud_user.update_user_active_status", return_value=None)

    # Act: Send update request for non-existent user
    response = await async_client.patch(
        "/api/v1/admin/users/999",
        json={
            "is_active": False
        }
    )

    # Assert: Verify not found response
    assert response.status_code == 404
    assert response.json() == {"detail": "使用者不存在"}


@pytest.mark.asyncio
async def test_update_user_missing_is_active_should_return_400(async_client: AsyncClient):
    """
    Test update without required is_active field should return 400.
    """
    # Act: Send request without is_active
    response = await async_client.patch(
        "/api/v1/admin/users/1",
        json={}
    )

    # Assert: Verify validation error
    assert response.status_code == 400  # Custom validation error handling


# --- Tests for DELETE /api/v1/admin/users/{id} ---

@pytest.mark.asyncio
async def test_delete_user_success_should_return_204(async_client: AsyncClient, mocker):
    """
    Test successful soft deletion of a user.
    """
    # Arrange: Mock successful soft delete
    deactivated_mock = MagicMock(**MOCK_ACTIVE_USER.__dict__)
    deactivated_mock.is_active = False
    mocker.patch("app.api.v1.endpoints.admin.crud_user.soft_delete_user", return_value=deactivated_mock)

    # Act: Send delete request
    response = await async_client.delete("/api/v1/admin/users/1")

    # Assert: Verify no content response
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_not_found_should_return_404(async_client: AsyncClient, mocker):
    """
    Test deletion of non-existent user should return 404.
    """
    # Arrange: Mock that the user doesn't exist
    mocker.patch("app.api.v1.endpoints.admin.crud_user.soft_delete_user", return_value=None)

    # Act: Send delete request for non-existent user
    response = await async_client.delete("/api/v1/admin/users/999")

    # Assert: Verify not found response
    assert response.status_code == 404
    assert response.json() == {"detail": "使用者不存在"}


# --- Security Tests ---

@pytest.mark.asyncio
async def test_user_response_should_never_include_password_hash(async_client: AsyncClient, mocker):
    """
    Test that all user-related API responses never include password_hash field.
    """
    # Mock user with password_hash field
    mock_user_with_password = MagicMock(
        id=1,
        username="test@example.com",
        password_hash="hashed_password_should_not_appear",
        invite_code_used="WELCOME2024",
        is_active=True,
        created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    
    # Test for single user endpoint
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_user_by_id", return_value=mock_user_with_password)
    response = await async_client.get("/api/v1/admin/users/1")
    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    
    # Test for users list endpoint
    mocker.patch("app.api.v1.endpoints.admin.crud_user.get_users", return_value=([mock_user_with_password], 1))
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    for user in data["items"]:
        assert "password_hash" not in user


# --- Edge Cases ---

@pytest.mark.asyncio
async def test_get_users_empty_list_should_return_200(async_client: AsyncClient, mocker):
    """
    Test retrieval of empty users list should return valid structure.
    """
    # Arrange: Mock empty response
    mocker.patch(
        "app.api.v1.endpoints.admin.crud_user.get_users",
        return_value=([], 0)
    )

    # Act: Send the request
    response = await async_client.get("/api/v1/admin/users")

    # Assert: Verify empty but valid response
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 1


@pytest.mark.asyncio
async def test_get_users_invalid_page_should_handle_gracefully(
    async_client: AsyncClient, mocker
):
    """
    Test handling of invalid pagination parameters.
    """
    # Arrange: Mock empty response for invalid page
    mocker.patch(
        "app.api.v1.endpoints.admin.crud_user.get_users",
        return_value=([], 0)
    )

    # Act: Send request with invalid page
    response = await async_client.get("/api/v1/admin/users?page=0")

    # Assert: Should handle validation error for invalid page
    assert response.status_code == 400
