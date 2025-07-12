"""
Test suite for the Invitation Code Management API endpoints.

This file contains comprehensive tests for the following APIs:
- POST /api/v1/admin/invitation-codes
- GET /api/v1/admin/invitation-codes
- PATCH /api/v1/admin/invitation-codes/{id}
- DELETE /api/v1/admin/invitation-codes/{id}

The tests follow Test-Driven Development (TDD) methodology and use pytest with mocking
to test the API logic in isolation.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from datetime import datetime, timezone


# --- Test Data Constants ---

# Mock invitation code objects for testing
MOCK_INVITATION_CODE = MagicMock(
    id=1,
    code="WELCOME2024",
    description="Welcome invitation code",
    is_active=True,
    expires_at=datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
    created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
)

MOCK_INVITATION_CODE_2 = MagicMock(
    id=2,
    code="SPECIAL2024",
    description="Special invitation code",
    is_active=False,
    expires_at=None,
    created_at=datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    updated_at=datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
)


# --- Tests for POST /api/v1/admin/invitation-codes ---

@pytest.mark.asyncio
async def test_create_invitation_code_success_should_return_201(async_client: AsyncClient, mocker):
    """
    Test successful creation of a new invitation code.
    """
    # Arrange: Mock the dependencies
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_code_by_code", return_value=None)
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.create_invitation_code", return_value=MOCK_INVITATION_CODE)

    # Act: Send the creation request
    response = await async_client.post(
        "/api/v1/admin/invitation-codes",
        json={
            "code": "WELCOME2024",
            "description": "Welcome invitation code",
            "expires_at": "2024-12-31T23:59:59Z"
        }
    )

    # Assert: Verify the response
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["code"] == "WELCOME2024"
    assert data["description"] == "Welcome invitation code"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_invitation_code_duplicate_should_return_409(async_client: AsyncClient, mocker):
    """
    Test creation with duplicate code should return 409 Conflict.
    """
    # Arrange: Mock that the code already exists
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_code_by_code", return_value=MOCK_INVITATION_CODE)

    # Act: Send the creation request
    response = await async_client.post(
        "/api/v1/admin/invitation-codes",
        json={
            "code": "WELCOME2024",
            "description": "Duplicate code"
        }
    )

    # Assert: Verify the conflict response
    assert response.status_code == 409
    assert response.json() == {"detail": "邀請碼已存在"}


@pytest.mark.asyncio
async def test_create_invitation_code_missing_code_should_return_400(async_client: AsyncClient):
    """
    Test creation without required code field should return 400 Bad Request.
    """
    # Act: Send request without code
    response = await async_client.post(
        "/api/v1/admin/invitation-codes",
        json={
            "description": "Missing code"
        }
    )

    # Assert: Verify validation error
    assert response.status_code == 400  # Custom validation error handling


@pytest.mark.asyncio
async def test_create_invitation_code_empty_code_should_return_400(async_client: AsyncClient):
    """
    Test creation with empty code should return 400 Bad Request.
    """
    # Act: Send request with empty code
    response = await async_client.post(
        "/api/v1/admin/invitation-codes",
        json={
            "code": "",
            "description": "Empty code"
        }
    )

    # Assert: Verify validation error
    assert response.status_code == 400  # Custom validation error handling


@pytest.mark.asyncio
async def test_create_invitation_code_empty_expires_at_should_return_201(async_client: AsyncClient, mocker):
    """
    Test creation with empty string expires_at should be converted to None and succeed.
    """
    # Arrange: Mock the dependencies
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_code_by_code", return_value=None)
    mock_created = MagicMock(
        id=1,
        code="TEST_EMPTY",
        description="Test empty expires_at",
        is_active=True,
        expires_at=None,  # Should be None after validation
        created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.create_invitation_code", return_value=mock_created)

    # Act: Send request with empty string expires_at
    response = await async_client.post(
        "/api/v1/admin/invitation-codes",
        json={
            "code": "TEST_EMPTY",
            "description": "Test empty expires_at",
            "expires_at": ""  # Empty string should be converted to None
        }
    )

    # Assert: Verify success
    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] is None


# --- Tests for GET /api/v1/admin/invitation-codes ---

@pytest.mark.asyncio
async def test_get_invitation_codes_success_should_return_200(async_client: AsyncClient, mocker):
    """
    Test successful retrieval of invitation codes list.
    """
    # Arrange: Mock the database response
    mock_codes = [MOCK_INVITATION_CODE, MOCK_INVITATION_CODE_2]
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_codes", return_value=(mock_codes, 2))

    # Act: Send the list request
    response = await async_client.get("/api/v1/admin/invitation-codes")

    # Assert: Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["pages"] == 1


@pytest.mark.asyncio
async def test_get_invitation_codes_with_active_filter_should_return_200(async_client: AsyncClient, mocker):
    """
    Test retrieval with active status filter.
    """
    # Arrange: Mock filtering for active codes only
    mock_codes = [MOCK_INVITATION_CODE]
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_codes", return_value=(mock_codes, 1))

    # Act: Send request with filter
    response = await async_client.get("/api/v1/admin/invitation-codes?is_active=true")

    # Assert: Verify the filtered response
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_invitation_codes_with_pagination_should_return_200(async_client: AsyncClient, mocker):
    """
    Test retrieval with pagination parameters.
    """
    # Arrange: Mock paginated response
    mock_codes = [MOCK_INVITATION_CODE]
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_codes", return_value=(mock_codes, 10))

    # Act: Send request with pagination
    response = await async_client.get("/api/v1/admin/invitation-codes?page=2&size=5")

    # Assert: Verify the paginated response
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 5
    assert data["pages"] == 2  # 10 total / 5 size = 2 pages


# --- Tests for PATCH /api/v1/admin/invitation-codes/{id} ---

@pytest.mark.asyncio
async def test_update_invitation_code_success_should_return_200(async_client: AsyncClient, mocker):
    """
    Test successful update of an invitation code.
    """
    # Arrange: Mock successful update
    updated_mock = MagicMock(
        id=1,
        code="WELCOME2024",
        description="Updated description",
        is_active=False,
        expires_at=None,
        created_at=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    )
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.update_invitation_code", return_value=updated_mock)

    # Act: Send the update request
    response = await async_client.patch(
        "/api/v1/admin/invitation-codes/1",
        json={
            "description": "Updated description",
            "is_active": False
        }
    )

    # Assert: Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["description"] == "Updated description"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_update_invitation_code_not_found_should_return_404(async_client: AsyncClient, mocker):
    """
    Test update of non-existent invitation code should return 404.
    """
    # Arrange: Mock that the code doesn't exist
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.update_invitation_code", return_value=None)

    # Act: Send update request for non-existent code
    response = await async_client.patch(
        "/api/v1/admin/invitation-codes/999",
        json={
            "description": "Updated description"
        }
    )

    # Assert: Verify not found response
    assert response.status_code == 404
    assert response.json() == {"detail": "邀請碼不存在"}


@pytest.mark.asyncio
async def test_update_invitation_code_partial_update_should_return_200(async_client: AsyncClient, mocker):
    """
    Test partial update (only one field) should work correctly.
    """
    # Arrange: Mock partial update
    updated_mock = MagicMock(**MOCK_INVITATION_CODE.__dict__)
    updated_mock.is_active = False
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.update_invitation_code", return_value=updated_mock)

    # Act: Send partial update
    response = await async_client.patch(
        "/api/v1/admin/invitation-codes/1",
        json={
            "is_active": False
        }
    )

    # Assert: Verify partial update response
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


# --- Tests for DELETE /api/v1/admin/invitation-codes/{id} ---

@pytest.mark.asyncio
async def test_delete_invitation_code_success_should_return_204(async_client: AsyncClient, mocker):
    """
    Test successful soft deletion of an invitation code.
    """
    # Arrange: Mock successful soft delete
    deactivated_mock = MagicMock(**MOCK_INVITATION_CODE.__dict__)
    deactivated_mock.is_active = False
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.soft_delete_invitation_code", return_value=deactivated_mock)

    # Act: Send delete request
    response = await async_client.delete("/api/v1/admin/invitation-codes/1")

    # Assert: Verify no content response
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_invitation_code_not_found_should_return_404(async_client: AsyncClient, mocker):
    """
    Test deletion of non-existent invitation code should return 404.
    """
    # Arrange: Mock that the code doesn't exist
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.soft_delete_invitation_code", return_value=None)

    # Act: Send delete request for non-existent code
    response = await async_client.delete("/api/v1/admin/invitation-codes/999")

    # Assert: Verify not found response
    assert response.status_code == 404
    assert response.json() == {"detail": "邀請碼不存在"}


# --- Edge Cases and Validation Tests ---

@pytest.mark.asyncio
async def test_get_invitation_codes_invalid_page_should_handle_gracefully(async_client: AsyncClient, mocker):
    """
    Test handling of invalid pagination parameters.
    """
    # Arrange: Mock empty response for invalid page
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.get_invitation_codes", return_value=([], 0))

    # Act: Send request with invalid page
    response = await async_client.get("/api/v1/admin/invitation-codes?page=0")

    # Assert: Should handle validation error for invalid page
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_invitation_code_empty_request_should_return_200(async_client: AsyncClient, mocker):
    """
    Test update with empty request body should return the unchanged object.
    """
    # Arrange: Mock update with no changes
    mocker.patch("app.api.v1.endpoints.admin.crud_invitation_code.update_invitation_code", return_value=MOCK_INVITATION_CODE)

    # Act: Send empty update
    response = await async_client.patch(
        "/api/v1/admin/invitation-codes/1",
        json={}
    )

    # Assert: Should return unchanged object
    assert response.status_code == 200