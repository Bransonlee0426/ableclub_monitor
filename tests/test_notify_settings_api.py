"""
Test suite for the Notification Settings API endpoints.

This file contains comprehensive tests for the notification settings CRUD API:
- POST /api/me/notify-settings (Create)
- GET /api/me/notify-settings (Read - List)
- PATCH /api/me/notify-settings/{id} (Update)
- DELETE /api/me/notify-settings/{id} (Delete)

The tests follow Test-Driven Development (TDD) methodology and include:
- Validation tests for conditional required fields
- Authorization tests (JWT token required)
- Business logic tests (duplicate prevention, ownership verification)
- Error handling tests
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


def get_auth_headers(user_id: int = 1) -> dict:
    """Helper function to get authorization headers with JWT token"""
    token = create_access_token(subject=str(user_id))
    return {"Authorization": f"Bearer {token}"}


# --- Tests for POST /api/me/notify-settings (Create) ---

class TestCreateNotifySetting:
    """Test cases for creating notification settings"""
    
    @pytest.mark.asyncio
    async def test_create_email_notify_setting_with_valid_data_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-001: Creating email notification setting with valid email should succeed
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_user_and_type", return_value=None)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.create_notify_setting", return_value=EMAIL_NOTIFY_SETTING_MOCK)
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
        assert data["data"]["notify_type"] == "email"
        assert data["data"]["email_address"] == "user@example.com"
        assert data["data"]["is_active"] is True
        assert "keywords" in data["data"]
        assert isinstance(data["data"]["keywords"], list)

    @pytest.mark.asyncio
    async def test_create_telegram_notify_setting_without_email_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-002: Creating non-email notification setting without email should succeed
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_user_and_type", return_value=None)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.create_notify_setting", return_value=TELEGRAM_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "telegram"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["notify_type"] == "telegram"
        assert data["data"]["email_address"] is None

    @pytest.mark.asyncio
    async def test_create_email_notify_setting_without_email_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-003: Creating email notification without email address should fail
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        response_data = response.json()
        # Check the custom error format
        assert response_data["success"] is False
        assert "參數驗證失敗" in response_data["message"]

    @pytest.mark.asyncio
    async def test_create_email_notify_setting_with_empty_email_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-004: Creating email notification with empty email should fail
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email", "email_address": ""},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "參數驗證失敗" in response_data["message"]

    @pytest.mark.asyncio
    async def test_create_notify_setting_with_empty_notify_type_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-005: Creating notification with empty notify_type should fail
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "", "email_address": "user@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "參數驗證失敗" in response_data["message"]

    @pytest.mark.asyncio
    async def test_create_duplicate_notify_setting_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-006: Creating duplicate notification setting should fail with 409 Conflict
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_user_and_type", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email", "email_address": "user@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 409
        assert response.json()["detail"] == "該通知類型的設定已存在"

    @pytest.mark.asyncio
    async def test_create_notify_setting_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test NST-007: Creating notification setting without JWT token should fail
        """
        # Act
        response = await async_client.post(
            "/api/v1/me/notify-settings/",
            json={"notify_type": "email", "email_address": "user@example.com"}
        )
        
        # Assert
        assert response.status_code == 401


# --- Tests for GET /api/me/notify-settings (Read - List) ---

class TestGetNotifySettings:
    """Test cases for listing notification settings"""
    
    @pytest.mark.asyncio
    async def test_get_user_notify_settings_should_return_list(self, async_client: AsyncClient, mocker):
        """
        Test NST-008: Getting user's notification settings should return formatted list
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_user_notify_settings", 
                    return_value=([EMAIL_NOTIFY_SETTING_MOCK, TELEGRAM_NOTIFY_SETTING_MOCK], 2))
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["notify_type"] == "email"
        assert data["items"][1]["notify_type"] == "telegram"

    @pytest.mark.asyncio
    async def test_get_notify_settings_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test NST-009: Getting notification settings without JWT token should fail
        """
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/")
        
        # Assert
        assert response.status_code == 401


# --- Tests for PATCH /api/me/notify-settings/{id} (Update) ---

class TestUpdateNotifySetting:
    """Test cases for updating notification settings"""
    
    @pytest.mark.asyncio
    async def test_update_notify_setting_valid_data_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-010: Updating notification setting with valid data should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        updated_setting.email_address = "newemail@example.com"
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update_notify_setting", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.patch(
            "/api/v1/me/notify-settings/1",
            json={"email_address": "newemail@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email_address"] == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_update_notify_setting_with_keywords_replacement_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-010B: Updating notification setting with keywords replacement should succeed
        """
        # Arrange: First create a setting with old keywords
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        updated_setting.email_address = "new@example.com"
        
        # Mock old keywords
        old_keyword_mock = MagicMock()
        old_keyword_mock.keyword = "old_keyword"
        
        # Mock new keywords after update
        new_keyword_mocks = [
            MagicMock(keyword="new1"),
            MagicMock(keyword="new2")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update_notify_setting", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=new_keyword_mocks)
        
        # Act: Send PUT request with keywords replacement
        response = await async_client.patch(
            "/api/v1/me/notify-settings/1",
            json={
                "email_address": "new@example.com",
                "keywords": ["new1", "new2"]
            },
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email_address"] == "new@example.com"
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["new1", "new2"]

    @pytest.mark.asyncio
    async def test_update_notify_setting_clear_keywords_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-010C: Updating notification setting to clear keywords should succeed
        """
        # Arrange: First create a setting with keywords
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        
        # Mock existing keyword that should be deleted
        existing_keyword_mock = MagicMock()
        existing_keyword_mock.keyword = "keyword_to_delete"
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update_notify_setting", return_value=updated_setting)
        # Mock empty keywords list after clearing
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act: Send PUT request with empty keywords array
        response = await async_client.patch(
            "/api/v1/me/notify-settings/1",
            json={"keywords": []},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == []

    @pytest.mark.asyncio
    async def test_update_nonexistent_notify_setting_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-011: Updating non-existent notification setting should fail with 404
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=None)
        
        # Act
        response = await async_client.patch(
            "/api/v1/me/notify-settings/999",
            json={"email_address": "newemail@example.com"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "找不到指定的通知設定"

    @pytest.mark.asyncio
    async def test_update_email_type_to_empty_email_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-012: Updating to email type with empty email should fail
        """
        # Arrange
        setting_without_email = MagicMock(**TELEGRAM_NOTIFY_SETTING_MOCK.__dict__)
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=setting_without_email)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=False)
        
        # Act
        response = await async_client.patch(
            "/api/v1/me/notify-settings/2",
            json={"notify_type": "email"},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Email 通知類型必須提供有效的 Email 地址"


# --- Tests for DELETE /api/me/notify-settings/{id} (Delete) ---

class TestDeleteNotifySetting:
    """Test cases for deleting notification settings"""
    
    @pytest.mark.asyncio
    async def test_delete_existing_notify_setting_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-013: Deleting existing notification setting should succeed with 200
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.delete_notify_setting", return_value=True)
        
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/1", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_nonexistent_notify_setting_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test NST-014: Deleting non-existent notification setting should fail with 404
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.delete_notify_setting", return_value=False)
        
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/999", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "找不到指定的通知設定"

    @pytest.mark.asyncio
    async def test_delete_notify_setting_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test NST-015: Deleting notification setting without JWT token should fail
        """
        # Act
        response = await async_client.delete("/api/v1/me/notify-settings/1")
        
        # Assert
        assert response.status_code == 401


# --- Tests for Keywords Integration ---

class TestNotifySettingsWithKeywords:
    """Test cases for notification settings with keywords integration"""
    
    @pytest.mark.asyncio
    async def test_get_notify_settings_should_include_keywords(self, async_client: AsyncClient, mocker):
        """
        Test NST-016: GET notify-settings should include user's keywords in each setting
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        
        # Mock notify settings with keywords
        notify_settings_with_keywords = [
            {
                "id": 1,
                "user_id": 1,
                "notify_type": "email",
                "email_address": "user@example.com",
                "is_active": True,
                "created_at": datetime(2024, 1, 1, 0, 0, 0),
                "updated_at": datetime(2024, 1, 1, 0, 0, 0),
                "keywords": ["Python", "FastAPI"]
            },
            {
                "id": 2,
                "user_id": 1,
                "notify_type": "telegram",
                "email_address": None,
                "is_active": True,
                "created_at": datetime(2024, 1, 1, 0, 0, 0),
                "updated_at": datetime(2024, 1, 1, 0, 0, 0),
                "keywords": ["Python", "FastAPI"]
            }
        ]
        
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_settings_with_keywords_by_user_id", 
                    return_value=(notify_settings_with_keywords, 2))
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        
        data = response_data["data"]
        assert data["total"] == 2
        assert len(data["items"]) == 2
        
        # Check first setting
        first_setting = data["items"][0]
        assert first_setting["notify_type"] == "email"
        assert first_setting["email_address"] == "user@example.com"
        assert "keywords" in first_setting
        assert first_setting["keywords"] == ["Python", "FastAPI"]
        
        # Check second setting
        second_setting = data["items"][1]
        assert second_setting["notify_type"] == "telegram"
        assert second_setting["email_address"] is None
        assert "keywords" in second_setting
        assert second_setting["keywords"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_get_notify_settings_with_no_keywords_should_include_empty_keywords(self, async_client: AsyncClient, mocker):
        """
        Test NST-017: GET notify-settings should include empty keywords list for users with no keywords
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        
        # Mock notify settings with empty keywords
        notify_settings_with_keywords = [
            {
                "id": 1,
                "user_id": 1,
                "notify_type": "email",
                "email_address": "user@example.com",
                "is_active": True,
                "created_at": datetime(2024, 1, 1, 0, 0, 0),
                "updated_at": datetime(2024, 1, 1, 0, 0, 0),
                "keywords": []
            }
        ]
        
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_settings_with_keywords_by_user_id", 
                    return_value=(notify_settings_with_keywords, 1))
        
        # Act
        response = await async_client.get("/api/v1/me/notify-settings/", headers=get_auth_headers())
        
        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        
        data = response_data["data"]
        assert data["total"] == 1
        assert len(data["items"]) == 1
        
        setting = data["items"][0]
        assert "keywords" in setting
        assert setting["keywords"] == []


# --- New Tests for Keywords Functionality ---

class TestKeywordsFunctionality:
    """Test cases specifically for keywords functionality in notification settings"""
    
    @pytest.mark.asyncio
    async def test_create_notify_setting_with_keywords_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-018: Creating notification setting with keywords should succeed
        """
        # Arrange
        keyword_mocks = [
            MagicMock(keyword="keyword1"),
            MagicMock(keyword="keyword2")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_user_and_type", return_value=None)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.create_notify_setting", return_value=EMAIL_NOTIFY_SETTING_MOCK)
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
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["keyword1", "keyword2"]

    @pytest.mark.asyncio
    async def test_update_notify_setting_replace_keywords_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-019: Updating notification setting to replace keywords should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        new_keyword_mocks = [
            MagicMock(keyword="new1"),
            MagicMock(keyword="new2")
        ]
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update_notify_setting", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=new_keyword_mocks)
        
        # Act
        response = await async_client.patch(
            "/api/v1/me/notify-settings/1",
            json={"keywords": ["new1", "new2"]},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == ["new1", "new2"]

    @pytest.mark.asyncio
    async def test_update_notify_setting_clear_keywords_with_empty_array_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test NST-020: Updating notification setting to clear all keywords with empty array should succeed
        """
        # Arrange
        updated_setting = MagicMock(**EMAIL_NOTIFY_SETTING_MOCK.__dict__)
        
        mocker.patch("dependencies.crud_user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.get_notify_setting_by_id", return_value=EMAIL_NOTIFY_SETTING_MOCK)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.validate_final_state", return_value=True)
        mocker.patch("app.api.v1.endpoints.notify_settings.crud_notify_setting.update_notify_setting", return_value=updated_setting)
        mocker.patch("app.api.v1.endpoints.notify_settings.get_by_user_id", return_value=[])
        
        # Act
        response = await async_client.patch(
            "/api/v1/me/notify-settings/1",
            json={"keywords": []},
            headers=get_auth_headers()
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "keywords" in data["data"]
        assert data["data"]["keywords"] == []