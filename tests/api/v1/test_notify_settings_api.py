"""
Test suite for the Singleton Resource Notification Settings API endpoints.

This file contains comprehensive tests for the new singleton resource notification settings API:
- POST /api/v1/me/notify-settings/ (Create)
- GET /api/v1/me/notify-settings/ (Read)
- PUT /api/v1/me/notify-settings/ (Update)
- DELETE /api/v1/me/notify-settings/ (Delete)

The tests follow Test-Driven Development (TDD) methodology and include:
- Validation tests for conditional required fields
- Authorization tests (JWT token required)
- Business logic tests (singleton pattern, conflict prevention)
- Error handling tests (404, 409, etc.)
- Keywords integration tests
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
from datetime import datetime

from core.security import create_access_token


# --- Test Data Constants ---

ACTIVE_USER_MOCK = MagicMock(
    id=1,
    username="user@example.com",
    password_hash="hashed_password",
    invite_code_used="TESTCODE",
    is_active=True,
    created_at=datetime(2024, 1, 1, 0, 0, 0),
    updated_at=datetime(2024, 1, 1, 0, 0, 0)
)

EMAIL_NOTIFY_SETTING_MOCK = MagicMock(
    id=1,
    user_id=1,
    notify_type="email",
    email_address="user@example.com",
    is_active=True,
    created_at=datetime(2024, 1, 1, 0, 0, 0),
    updated_at=datetime(2024, 1, 1, 0, 0, 0)
)

TELEGRAM_NOTIFY_SETTING_MOCK = MagicMock(
    id=2,
    user_id=1,
    notify_type="telegram",
    email_address=None,
    is_active=True,
    created_at=datetime(2024, 1, 1, 0, 0, 0),
    updated_at=datetime(2024, 1, 1, 0, 0, 0)
)


def get_auth_headers(username: str = "user@example.com") -> dict:
    """Helper function to get authorization headers with JWT token"""
    token = create_access_token(subject=username)
    return {"Authorization": f"Bearer {token}"}


# --- Tests for POST /api/v1/me/notify-settings/ (Create) ---

class TestCreateNotifySetting:
    """Test cases for creating notification settings using Singleton Resource pattern"""
    
    @pytest.mark.asyncio
    async def test_create_email_notify_setting_with_valid_data_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-001: Creating email notification setting with valid email should succeed (200 OK)
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=None)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.create_with_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={
                "notify_type": "email", 
                "email_address": "user@example.com",
                "keywords": ["keyword1", "keyword2"]
            },
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["notify_type"] == "email"
        assert data["data"]["email_address"] == "user@example.com"
        assert data["data"]["is_active"] is True
        assert "keywords" in data["data"]
        assert isinstance(data["data"]["keywords"], list)

    @pytest.mark.asyncio
    async def test_create_notify_setting_when_already_exists_should_return_409_conflict(self, async_client: AsyncClient, mocker):
        """
        Test NST-002: Creating notification setting when one already exists should return 409 Conflict
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email", "email_address": "user@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 409
        assert response.json()["detail"] == "Notify setting already exists for this user."

    @pytest.mark.asyncio
    async def test_create_email_notify_setting_without_email_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-003: Creating email notification without email address should fail with validation error
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "參數驗證失敗" in response_data["message"]

    @pytest.mark.asyncio
    async def test_create_notify_setting_without_token_should_return_401_unauthorized(self, async_client: AsyncClient):
        """
        Test NST-004: Creating notification setting without JWT token should return 401 Unauthorized
        """
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email", "email_address": "user@example.com"}
        )
        
        # Assert
        assert response.status_code == 401


# --- Tests for GET /api/v1/me/notify-settings/ (Read) ---

class TestReadNotifySetting:
    """Test cases for reading notification settings using Singleton Resource pattern"""
    
    @pytest.mark.asyncio
    async def test_get_existing_notify_setting_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-005: Getting existing notification setting should return setting data
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["notify_type"] == "email"
        assert data["data"]["email_address"] == "user@example.com"
        assert "keywords" in data["data"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_notify_setting_should_return_404_not_found(self, async_client: AsyncClient, mocker):
        """
        Test NST-006: Getting non-existent notification setting should return 404 Not Found
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=None)
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "找不到通知設定"

    @pytest.mark.asyncio
    async def test_get_notify_setting_without_token_should_return_401_unauthorized(self, async_client: AsyncClient):
        """
        Test NST-007: Getting notification setting without JWT token should return 401 Unauthorized
        """
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/")
        
        # Assert
        assert response.status_code == 401


# --- Tests for PUT /api/v1/me/notify-settings/ (Update) ---

class TestUpdateNotifySetting:
    """Test cases for updating notification settings using Singleton Resource pattern"""
    
    @pytest.mark.asyncio
    async def test_update_existing_notify_setting_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-008: Updating existing notification setting with valid data should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        updated_setting.email_address = "newemail@example.com"
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.put(
            "/api/v1/me/notify-settings/",
            json={"email_address": "newemail@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email_address"] == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_update_nonexistent_notify_setting_should_return_404_not_found(self, async_client: AsyncClient, mocker):
        """
        Test NST-009: Updating non-existent notification setting should return 404 Not Found
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=None)
        
        # Act
        response = await async_client.put(
            "/api/v1/me/notify-settings/",
            json={"email_address": "newemail@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "找不到通知設定"

    @pytest.mark.asyncio
    async def test_update_to_invalid_email_state_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-010: Updating to invalid email state should fail with validation error
        """
        # Arrange
        setting_without_email = MagicMock(**TELEGRAM_NOTIFY_SETTING_MOCK.__dict__)
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=setting_without_email)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=False)
        
        # Act
        response = await async_client.put(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Email 通知類型必須提供有效的 Email 地址"

    @pytest.mark.asyncio
    async def test_update_notify_setting_with_keywords_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-011: Updating notification setting with keywords should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        new_keyword_mocks = [
            MagicMock(keyword="new1"),
            MagicMock(keyword="new2")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=new_keyword_mocks)
        
        # Act
        response = await async_client.put(
            "/api/v1/me/notify-settings/",
            json={"keywords": ["new1", "new2"]},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["new1", "new2"]


# --- Tests for DELETE /api/v1/me/notify-settings/ (Delete) ---

class TestDeleteNotifySetting:
    """Test cases for deleting notification settings using Singleton Resource pattern"""
    
    @pytest.mark.asyncio
    async def test_delete_existing_notify_setting_should_return_204_no_content(self, async_client: AsyncClient, mocker):
        """
        Test NST-012: Deleting existing notification setting should return 204 No Content
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.remove_by_owner", return_value=True)
        
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 204
        # 204 No Content should have empty body
        assert response.content == b""

    @pytest.mark.asyncio
    async def test_delete_nonexistent_notify_setting_should_return_404_not_found(self, async_client: AsyncClient, mocker):
        """
        Test NST-013: Deleting non-existent notification setting should return 404 Not Found
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=None)
        
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "找不到通知設定"

    @pytest.mark.asyncio
    async def test_delete_notify_setting_without_token_should_return_401_unauthorized(self, async_client: AsyncClient):
        """
        Test NST-014: Deleting notification setting without JWT token should return 401 Unauthorized
        """
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/")
        
        # Assert
        assert response.status_code == 401


# --- Tests for Keywords Integration ---

class TestNotifySettingsWithKeywords:
    """Test cases for notification settings with keywords integration in Singleton Resource pattern"""
    
    @pytest.mark.asyncio
    async def test_create_notify_setting_with_keywords_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-015: Creating notification setting with keywords should succeed
        """
        # Arrange
        keyword_mocks = [
            MagicMock(keyword="keyword1"),
            MagicMock(keyword="keyword2")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=None)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.create_with_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=keyword_mocks)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={
                "notify_type": "email",
                "email_address": "user@example.com",
                "keywords": ["keyword1", "keyword2"]
            },
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["keyword1", "keyword2"]

    @pytest.mark.asyncio
    async def test_get_notify_setting_should_include_keywords(self, async_client: AsyncClient, mocker):
        """
        Test NST-016: GET notify-setting should include user's keywords
        """
        # Arrange
        keyword_mocks = [
            MagicMock(keyword="Python"),
            MagicMock(keyword="FastAPI")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=keyword_mocks)
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_get_notify_setting_with_no_keywords_should_include_empty_keywords(self, async_client: AsyncClient, mocker):
        """
        Test NST-017: GET notify-setting should include empty keywords list for users with no keywords
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == []

    @pytest.mark.asyncio
    async def test_update_notify_setting_clear_keywords_with_empty_array_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-018: Updating notification setting to clear all keywords with empty array should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_by_owner", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.put(
            "/api/v1/me/notify-settings/",
            json={"keywords": []},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == []