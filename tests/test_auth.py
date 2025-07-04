import pytest
from httpx import AsyncClient
from unittest.mock import patch

from api.dependencies.auth import create_access_token

pytestmark = pytest.mark.asyncio

async def test_signup_success(client: AsyncClient):
    """
    Test successful user signup.
    """
    response = await client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "ValidPassword1!",
        "username": "testuser"
    })
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert response_data["email"] == "test@example.com"
    assert response_data["username"] == "testuser"
    assert "password" not in response_data

async def test_signup_duplicate_email(client: AsyncClient):
    """
    Test that signup fails if the email already exists.
    """
    # First, create a user
    await client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "ValidPassword1!",
        "username": "testuser"
    })

    # Then, try to create a user with the same email
    response = await client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "AnotherPassword1!",
        "username": "anotheruser"
    })

    assert response.status_code == 400
    assert "Email or username already exists" in response.text

async def test_login_success(client: AsyncClient):
    """
    Test successful user login.
    """
    # First, create a user
    await client.post("/auth/signup", json={
        "email": "login@example.com",
        "password": "ValidPassword1!",
        "username": "loginuser"
    })

    # Then, log in with the same credentials
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "ValidPassword1!"
    })

    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

async def test_login_wrong_password(client: AsyncClient):
    """
    Test that login fails with an incorrect password.
    """
    # First, create a user
    await client.post("/auth/signup", json={
        "email": "wrongpass@example.com",
        "password": "ValidPassword1!",
        "username": "wrongpassuser"
    })

    # Then, try to log in with the wrong password
    response = await client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "WrongPassword!"
    })

    assert response.status_code == 401
    assert "Invalid credentials" in response.text

async def test_login_user_not_found(client: AsyncClient):
    """
    Test that login fails if the user does not exist.
    """
    response = await client.post("/auth/login", json={
        "email": "nouser@example.com",
        "password": "ValidPassword1!"
    })

    assert response.status_code == 401
    assert "Invalid credentials" in response.text

@patch("fastapi_mail.FastMail.send_message")
async def test_forgot_password_success(mock_send_message, client: AsyncClient):
    """
    Test successful password reset request.
    """
    # Create a user first
    signup_data = {
        "email": "forgotpass@example.com",
        "password": "ValidPassword1!",
        "username": "forgotpassuser",
    }
    await client.post("/auth/signup", json=signup_data)

    # Request password reset
    response = await client.post(
        "/auth/forgot-password", json={"email": "forgotpass@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent"}
    mock_send_message.assert_called_once()

async def test_forgot_password_user_not_found(client: AsyncClient):
    """
    Test password reset request for a non-existent user.
    """
    response = await client.post(
        "/auth/forgot-password", json={"email": "nonexistent@example.com"}
    )

    assert response.status_code == 404
    assert "User not found" in response.text

async def test_reset_password_success(client: AsyncClient):
    """
    Test successful password reset and login with the new password.
    """
    # 1. Create a user
    signup_data = {
        "email": "resetpass@example.com",
        "password": "OldPassword1!",
        "username": "resetpassuser",
    }
    signup_response = await client.post("/auth/signup", json=signup_data)
    user_id = signup_response.json()["id"]

    # 2. Generate a reset token for the user
    reset_token = create_access_token(data={"sub": user_id})

    # 3. Reset the password
    new_password = "NewPassword1!"
    reset_response = await client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password,
        },
    )
    assert reset_response.status_code == 200
    assert reset_response.json() == {"message": "Password has been reset successfully"}

    # 4. Try to log in with the new password
    login_response = await client.post(
        "/auth/login",
        json={"email": "resetpass@example.com", "password": new_password},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

async def test_reset_password_invalid_token(client: AsyncClient):
    """
    Test password reset with an invalid token.
    """
    response = await client.post(
        "/auth/reset-password",
        json={
            "token": "invalidtoken",
            "new_password": "NewPassword1!",
            "confirm_password": "NewPassword1!",
        },
    )
    assert response.status_code == 401
    assert "Invalid token" in response.text

async def test_reset_password_mismatch(client: AsyncClient):
    """
    Test password reset with mismatching new passwords.
    """
    # 1. Create a user and token
    signup_response = await client.post(
        "/auth/signup",
        json={
            "email": "mismatch@example.com",
            "password": "OldPassword1!",
            "username": "mismatchuser",
        },
    )
    user_id = signup_response.json()["id"]
    reset_token = create_access_token(data={"sub": user_id})

    # 2. Attempt to reset with mismatching passwords
    response = await client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": "NewPassword1!",
            "confirm_password": "DifferentPassword1!",
        },
    )
    assert response.status_code == 422  # Unprocessable Entity for validation error
    assert "Passwords do not match" in response.text
