"""
Test suite for the Authentication and User API endpoints.

This file contains a comprehensive set of tests for the following APIs:
- POST /api/v1/auth/login-or-register
- GET /api/v1/users/check-status

The tests are written following the Test-Driven Development (TDD) methodology.
They use pytest and pytest-mock to simulate database interactions and security functions,
ensuring that the API logic is tested in isolation without depending on a live database.

Each test function corresponds to a specific test case defined in the product specification.
The naming convention for test functions is `test_{endpoint}_{scenario}_should_{expected_outcome}`.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock

# --- Test Data Constants ---
# These constants are used across multiple tests to ensure consistency.

# A mock user object that represents an existing, active user in the database.
EXISTING_USER_MOCK = MagicMock(
    username="exist@user.com",
    password_hash="hashed_password_for_goodpassword",
    is_active=True
)

# A mock user object for an account that has been deactivated.
INACTIVE_USER_MOCK = MagicMock(
    username="inactive@user.com",
    password_hash="hashed_password_for_goodpassword",
    is_active=False
)

# A mock object for a valid and active invitation code.
VALID_INVITE_CODE_MOCK = MagicMock(
    code="VALIDCODE",
    is_active=True
)


# --- Tests for POST /api/v1/auth/login-or-register ---

@pytest.mark.asyncio
async def test_lor_001_register_new_user_with_valid_code_should_succeed(async_client: AsyncClient, mocker):
    """
    Tests LOR-001: Successful registration for a new user with a valid invitation code.
    """
    # Arrange: Mock the dependencies for the registration success path.
    # 1. The user does not exist in the database.
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=None)
    # 2. The invitation code is valid.
    mocker.patch("app.api.v1.endpoints.auth.crud_invitation_code.get_valid_code", return_value=VALID_INVITE_CODE_MOCK)
    # 3. The user creation function will return a new user object.
    mocker.patch("app.api.v1.endpoints.auth.crud_user.create_user", return_value=MagicMock(username="test@user.com"))
    # 4. The token creation function will return a mock token.
    mocker.patch("app.api.v1.endpoints.auth.security.create_access_token", return_value="mock_jwt_token")

    # Act: Send the registration request.
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "test@user.com", "password": "goodpassword", "inviteCode": "VALIDCODE"}
    )

    # Assert: Verify the response matches the specification for successful registration.
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "註冊成功"
    assert "token" in data
    assert data["token"]["access_token"] == "mock_jwt_token"
    assert data["token"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_lor_002_login_existing_user_with_correct_password_should_succeed(async_client: AsyncClient, mocker):
    """
    Tests LOR-002: Successful login for an existing user with the correct password.
    """
    # Arrange: Mock dependencies for the login success path.
    # 1. The user exists and is active.
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=EXISTING_USER_MOCK)
    # 2. The password verification succeeds.
    mocker.patch("app.api.v1.endpoints.auth.security.verify_password", return_value=True)
    # 3. A token is created.
    mocker.patch("app.api.v1.endpoints.auth.security.create_access_token", return_value="mock_jwt_token")

    # Act: Send the login request.
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "exist@user.com", "password": "goodpassword"}
    )

    # Assert: Verify the response for successful login.
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "登入成功"
    assert "token" in data


@pytest.mark.asyncio
async def test_lor_003_register_new_user_without_invite_code_should_fail(async_client: AsyncClient, mocker):
    """
    Tests LOR-003: A new user trying to register without an invite code should be rejected.
    """
    # Arrange: The user does not exist.
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=None)

    # Act: Send request without inviteCode.
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "new@user.com", "password": "goodpassword"}
    )

    # Assert: Verify the specific error for missing invite code.
    assert response.status_code == 402
    assert response.json() == {"detail": "您尚未註冊，請輸入邀請碼"}


@pytest.mark.asyncio
@pytest.mark.parametrize("code, mock_return", [
    ("FAKECODE", None),  # LOR-004: Code does not exist
    ("INACTIVECODE", MagicMock(is_active=False)),  # LOR-005: Code is inactive
])
async def test_lor_004_005_register_with_invalid_or_inactive_code_should_fail(async_client: AsyncClient, mocker, code, mock_return):
    """
    Tests LOR-004 & LOR-005: Registration fails if the invite code is non-existent or inactive.
    """
    # Arrange
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=None)
    mocker.patch("app.api.v1.endpoints.auth.crud_invitation_code.get_valid_code", return_value=mock_return)

    # Act
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "new@user.com", "password": "goodpassword", "inviteCode": code}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "邀請碼無效。"}


@pytest.mark.asyncio
async def test_lor_006_login_with_wrong_password_should_fail(async_client: AsyncClient, mocker):
    """
    Tests LOR-006: Login fails for an existing user with an incorrect password.
    """
    # Arrange
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=EXISTING_USER_MOCK)
    mocker.patch("app.api.v1.endpoints.auth.security.verify_password", return_value=False) # Password mismatch

    # Act
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "exist@user.com", "password": "wrongpassword"}
    )

    # Assert
    assert response.status_code == 401
    assert response.json() == {"detail": "密碼錯誤、請重新確認。"}


@pytest.mark.asyncio
async def test_lor_007_login_with_inactive_account_should_fail(async_client: AsyncClient, mocker):
    """
    Tests LOR-007: Login fails if the user's account has been deactivated.
    """
    # Arrange: The user exists but is inactive.
    mocker.patch("app.api.v1.endpoints.auth.crud_user.get_user_by_username", return_value=INACTIVE_USER_MOCK)

    # Act
    response = await async_client.post(
        "/api/v1/auth/login-or-register",
        json={"username": "inactive@user.com", "password": "goodpassword"}
    )

    # Assert: The error should be the same as a wrong password to avoid leaking user status.
    assert response.status_code == 401
    assert response.json() == {"detail": "密碼錯誤、請重新確認。"}


@pytest.mark.asyncio
@pytest.mark.parametrize("payload, expected_message, expected_status_code", [
    ({"username": "", "password": "password123"}, "帳號錯誤、請重新確認。", 400), # LOR-008
    ({"username": "user@test.com", "password": ""}, "密碼錯誤、請重新確認。", 400), # LOR-009
    ({"username": "not-an-email", "password": "password123"}, "帳號錯誤、請重新確認。", 400), # LOR-010
])
async def test_lor_008_010_validation_checks_should_fail(async_client: AsyncClient, payload, expected_message, expected_status_code):
    """
    Tests LOR-008, LOR-009, LOR-010: Validation for empty or malformed username/password.
    """
    # Act
    response = await async_client.post("/api/v1/auth/login-or-register", json=payload)

    # Assert
    assert response.status_code == expected_status_code
    assert response.json() == {"success": False, "message": expected_message}


# --- Tests for GET /api/v1/users/check-status ---

@pytest.mark.asyncio
async def test_chk_001_check_status_for_registered_user_should_return_true(async_client: AsyncClient, mocker):
    """
    Tests CHK-001: Checking status for a registered and active user.
    """
    # Arrange: User exists and is active.
    mocker.patch("app.api.v1.endpoints.users.crud_user.get_user_by_username", return_value=EXISTING_USER_MOCK)

    # Act
    response = await async_client.get("/api/v1/users/check-status?username=exist@user.com")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] == True
    assert response_data["message"] == "查詢成功"
    assert response_data["data"]["isRegistered"] == True


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_return", [
    (None),  # CHK-002: User does not exist
    (INACTIVE_USER_MOCK),  # CHK-003: User is inactive
])
async def test_chk_002_003_check_status_for_unregistered_or_inactive_user_should_return_false(async_client: AsyncClient, mocker, mock_return):
    """
    Tests CHK-002 & CHK-003: Status check for a non-existent or inactive user should return false.
    """
    # Arrange
    mocker.patch("app.api.v1.endpoints.users.crud_user.get_user_by_username", return_value=mock_return)

    # Act
    response = await async_client.get("/api/v1/users/check-status?username=nonexist@user.com")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] == True
    assert response_data["message"] == "查詢成功"
    assert response_data["data"]["isRegistered"] == False


@pytest.mark.asyncio
async def test_chk_004_check_status_without_username_should_fail(async_client: AsyncClient):
    """
    Tests CHK-004: Requesting status without a username query parameter should result in a validation error.
    """
    # Act
    response = await async_client.get("/api/v1/users/check-status")

    # Assert: The custom validation handler should return a 400 Bad Request.
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["success"] == False
    assert response_data["message"] == "帳號錯誤、請重新確認。"
    assert response_data["error_code"] == "VALIDATION_ERROR"
