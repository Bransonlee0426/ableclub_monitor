"""
Test suite for JWT Authentication Security System.

This file contains comprehensive tests for the JWT authentication and authorization functionality,
following Test-Driven Development (TDD) methodology.

The tests are divided into two main parts:
1. Unit tests for the verify_and_decode_token function
2. Integration tests for protected endpoints

Each test function corresponds to a specific scenario defined in the TDD specification.
The naming convention is: test_{functionality}_{scenario}_should_{expected_outcome}
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import jwt

from core.security import create_access_token
from core.config import settings


# --- Test Data Constants ---
# Mock user objects for different test scenarios

ACTIVE_USER_MOCK = MagicMock(
    id=1,
    username="active@user.com",
    password_hash="hashed_password",
    invite_code_used="TESTCODE",
    is_active=True,
    created_at=datetime(2024, 1, 1, 0, 0, 0),
    updated_at=datetime(2024, 1, 1, 0, 0, 0)
)

INACTIVE_USER_MOCK = MagicMock(
    id=2,
    username="inactive@user.com",
    password_hash="hashed_password",
    invite_code_used="TESTCODE",
    is_active=False,
    created_at=datetime(2024, 1, 1, 0, 0, 0),
    updated_at=datetime(2024, 1, 1, 0, 0, 0)
)


# --- Part 1.1: Unit Tests for verify_and_decode_token Function ---

class TestVerifyAndDecodeToken:
    """
    Unit tests for the verify_and_decode_token function in core/security.py
    """
    
    def test_decode_valid_token_should_return_user_id(self, mocker):
        """
        Test TST-001: A valid, non-expired token should return the user_id from the sub field.
        """
        # Arrange: Create a valid token for user_id=1
        user_id = 1
        token = create_access_token(subject=str(user_id))
        
        # Import the function that should be implemented
        from core.security import verify_and_decode_token
        
        # Act: Decode the token
        result = verify_and_decode_token(token)
        
        # Assert: Should return the user_id as integer
        assert result == user_id
        assert isinstance(result, int)

    def test_decode_expired_token_should_raise_exception(self, mocker):
        """
        Test TST-002: An expired token should raise HTTPException with 401 status code.
        """
        # Arrange: Create an expired token
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_payload = {
            "sub": "1",
            "exp": past_time
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Import the function
        from core.security import verify_and_decode_token
        
        # Act & Assert: Should raise HTTPException with 401 status
        with pytest.raises(HTTPException) as exc_info:
            verify_and_decode_token(expired_token)
        
        assert exc_info.value.status_code == 401
        assert "憑證無效或已過期" in exc_info.value.detail

    def test_decode_invalid_signature_token_should_raise_exception(self, mocker):
        """
        Test TST-003: A token with invalid signature should raise HTTPException with 401 status code.
        """
        # Arrange: Create a token with wrong secret key
        wrong_payload = {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=1)}
        invalid_token = jwt.encode(wrong_payload, "wrong_secret_key", algorithm=settings.ALGORITHM)
        
        # Import the function
        from core.security import verify_and_decode_token
        
        # Act & Assert: Should raise HTTPException with 401 status
        with pytest.raises(HTTPException) as exc_info:
            verify_and_decode_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "憑證無效或已過期" in exc_info.value.detail

    def test_decode_token_with_missing_sub_should_raise_exception(self, mocker):
        """
        Test TST-004: A token without 'sub' field should raise HTTPException with 401 status code.
        """
        # Arrange: Create a token without 'sub' field
        payload_without_sub = {"exp": datetime.utcnow() + timedelta(hours=1)}
        token_without_sub = jwt.encode(payload_without_sub, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Import the function
        from core.security import verify_and_decode_token
        
        # Act & Assert: Should raise HTTPException with 401 status
        with pytest.raises(HTTPException) as exc_info:
            verify_and_decode_token(token_without_sub)
        
        assert exc_info.value.status_code == 401
        assert "憑證無效或已過期" in exc_info.value.detail


# --- Part 1.2: Integration Tests for Protected Endpoints ---

class TestProtectedEndpoints:
    """
    Integration tests for protected API endpoints that require JWT authentication
    """
    
    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_valid_token_should_succeed(self, async_client: AsyncClient, mocker):
        """
        Test TST-005: Accessing protected resource with valid token should return user data.
        """
        # Arrange: Mock database to return active user
        mocker.patch("crud.user.get_user_by_id", return_value=ACTIVE_USER_MOCK)
        
        # Create valid token for user_id=1
        token = create_access_token(subject="1")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Act: Request protected endpoint
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        # Assert: Should return 200 OK with user data
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "active@user.com"
        assert data["is_active"] is True
        assert "password_hash" not in data  # Security: password should not be exposed

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_without_token_should_fail(self, async_client: AsyncClient):
        """
        Test TST-006: Accessing protected resource without token should return 401 Unauthorized.
        """
        # Act: Request protected endpoint without Authorization header
        response = await async_client.get("/api/v1/users/me")
        
        # Assert: Should return 401 Unauthorized
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_access_protected_endpoint_with_inactive_user_token_should_fail(self, async_client: AsyncClient, mocker):
        """
        Test TST-007: Using token of inactive user should return 400 Bad Request.
        """
        # Arrange: Mock database to return inactive user
        mocker.patch("crud.user.get_user_by_id", return_value=INACTIVE_USER_MOCK)
        
        # Create valid token for inactive user_id=2
        token = create_access_token(subject="2")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Act: Request protected endpoint
        response = await async_client.get("/api/v1/users/me", headers=headers)
        
        # Assert: Should return 400 Bad Request for inactive user
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "使用者帳號已被停用"