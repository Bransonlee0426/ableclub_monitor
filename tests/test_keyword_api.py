"""
Test suite for the Keywords API endpoints.

This file contains comprehensive tests for the Keywords API endpoints
"""
import pytest
from httpx import AsyncClient
from schemas.response import SuccessResponse
from typing import List
from core.security import create_access_token


class TestGetKeywords:
    """
    Test cases for GET /api/v1/me/keywords/ endpoint
    """

    @pytest.mark.asyncio
    async def test_get_keywords_for_new_user_should_return_empty_list(self, async_client: AsyncClient, mocker):
        """
        Test KWT-001: Getting keywords for a new user should return empty list
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.keywords.crud_keyword.get_by_user_id", return_value=[])

        # Act
        response = await async_client.get("/api/v1/me/keywords/", headers=get_auth_headers())

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "查詢成功"
        assert data["data"] == []
        assert data["error_code"] is None

    @pytest.mark.asyncio
    async def test_get_keywords_should_return_user_keywords_list(self, async_client: AsyncClient, mocker):
        """
        Test KWT-002: Getting keywords should return user's keywords list
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mock_keywords = [
            MockKeyword(keyword="Python"),
            MockKeyword(keyword="FastAPI"),
            MockKeyword(keyword="測試")
        ]
        mocker.patch("app.api.v1.endpoints.keywords.crud_keyword.get_by_user_id", return_value=mock_keywords)

        # Act
        response = await async_client.get("/api/v1/me/keywords/", headers=get_auth_headers())

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "查詢成功"
        assert data["data"] == ["Python", "FastAPI", "測試"]
        assert data["error_code"] is None

    @pytest.mark.asyncio
    async def test_get_keywords_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test KWT-003: Getting keywords without authentication should fail
        """
        # Act
        response = await async_client.get("/api/v1/me/keywords/")

        # Assert
        assert response.status_code == 403  # 沒有 Token 會回傳 403 Forbidden


class TestUpdateKeywords:
    """
    Test cases for PUT /api/v1/me/keywords/ endpoint
    """

    @pytest.mark.asyncio
    async def test_update_keywords_with_put_should_replace_all_keywords(self, async_client: AsyncClient, mocker):
        """
        Test KWT-004: PUT should completely replace user's keywords list
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        updated_keywords = [
            MockKeyword(keyword="Python"),
            MockKeyword(keyword="FastAPI")
        ]
        mocker.patch("app.api.v1.endpoints.keywords.crud_keyword.sync_for_user", return_value=updated_keywords)

        # Act
        response = await async_client.put(
            "/api/v1/me/keywords/", 
            json=["Python", "FastAPI"],
            headers=get_auth_headers()
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "關鍵字更新成功"
        assert data["data"] == ["Python", "FastAPI"]
        assert data["error_code"] is None

    @pytest.mark.asyncio
    async def test_update_keywords_is_idempotent(self, async_client: AsyncClient, mocker):
        """
        Test KWT-005: PUT operations should be idempotent
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        keywords = [MockKeyword(keyword="React")]
        mocker.patch("app.api.v1.endpoints.keywords.crud_keyword.sync_for_user", return_value=keywords)

        # Act - 執行兩次相同的請求
        response1 = await async_client.put(
            "/api/v1/me/keywords/", 
            json=["React"],
            headers=get_auth_headers()
        )
        response2 = await async_client.put(
            "/api/v1/me/keywords/", 
            json=["React"],
            headers=get_auth_headers()
        )

        # Assert - 兩次結果應該相同
        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert data1["success"] is True
        assert data2["success"] is True
        assert data1["message"] == "關鍵字更新成功"
        assert data2["message"] == "關鍵字更新成功"
        assert data1["data"] == ["React"]
        assert data2["data"] == ["React"]

    @pytest.mark.asyncio
    async def test_update_keywords_with_empty_list_should_clear_all(self, async_client: AsyncClient, mocker):
        """
        Test KWT-006: PUT with empty list should clear all keywords
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)
        mocker.patch("app.api.v1.endpoints.keywords.crud_keyword.sync_for_user", return_value=[])

        # Act
        response = await async_client.put(
            "/api/v1/me/keywords/", 
            json=[],
            headers=get_auth_headers()
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "關鍵字更新成功"
        assert data["data"] == []
        assert data["error_code"] is None

    @pytest.mark.asyncio
    async def test_update_keywords_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test KWT-007: PUT keywords without authentication should fail
        """
        # Act
        response = await async_client.put("/api/v1/me/keywords/", json=["Python"])

        # Assert
        assert response.status_code == 403  # 沒有 Token 會回傳 403 Forbidden

    @pytest.mark.asyncio
    async def test_update_keywords_with_invalid_json_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test KWT-008: PUT with invalid JSON should return validation error
        """
        # Arrange
        mocker.patch("dependencies.crud_user.get_user_by_username", return_value=ACTIVE_USER_MOCK)

        # Act - 發送無效的 JSON 結構（應該是字串列表，但送了字典）
        response = await async_client.put(
            "/api/v1/me/keywords/", 
            json={"invalid": "format"},
            headers=get_auth_headers()
        )

        # Assert
        assert response.status_code == 400  # 資料驗證錯誤


# Test fixtures and helpers
class MockKeyword:
    def __init__(self, keyword: str):
        self.keyword = keyword


class MockUser:
    def __init__(self, id: int, username: str, is_active: bool = True):
        self.id = id
        self.username = username
        self.is_active = is_active


ACTIVE_USER_MOCK = MockUser(id=1, username="test@example.com", is_active=True)


def get_auth_headers(user_id: int = 1):
    """Get authentication headers for testing"""
    token = create_access_token(subject=str(user_id))
    return {"Authorization": f"Bearer {token}"} 