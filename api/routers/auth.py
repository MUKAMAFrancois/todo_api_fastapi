# auth router
from fastapi import APIRouter, Depends, HTTPException, status
from api.dependencies.database import get_db
from api.models.user import User
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import EmailStr
from typing import Annotated
from core.config import settings
from api.dependencies.auth import create_access_token
from api.utils.password import get_password_hash, verify_password
from api.schemas.user import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    UserSignupResponse, 
    Token, 
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse
)
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta
from bson import ObjectId
from api.services.email import send_reset_password_email
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
# timedelta is used to calculate the expiry time of the token.

router = APIRouter(prefix="/auth", tags=["auth"])

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # bcrypt is a password hashing algorithm. deprecated="auto" is used to use the latest version of the algorithm.

# endpoints
# Signup
@router.post(
    "/signup", 
    response_model=UserSignupResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with a unique email and username."
)
async def signup(user: UserCreate, db: Annotated[AsyncIOMotorClient, Depends(get_db)]):
    """
    Signs up a new user.
    """
    # check if user already exists
    existing_user = await db["users"].find_one(
        {"$or": [{"email": user.email}, {"username": user.username}]}
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Email or username already exists"
        )

    user_data = user.model_dump()
    user_data["password"] = get_password_hash(user_data["password"])

    # insert user into database
    result = await db["users"].insert_one(user_data)

    # retrieve the created user
    created_user = await db["users"].find_one({"_id": result.inserted_id})

    return created_user


# Login
@router.post(
    "/login", 
    response_model=Token, 
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate a user and return a JWT access token."
)
async def login(form_data: UserLogin, db:Annotated[AsyncIOMotorClient,Depends(get_db)]):
    """
    Logs in a user.
    """
    # check if user exists
    user = await db["users"].find_one({"email": form_data.email})
    if not user or "password" not in user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }

# Forgot Password
@router.post(
    "/forgot-password", 
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a password reset email",
    description="Send a password reset link to the user's email address."
)
async def forgot_password(request: ForgotPasswordRequest, db:Annotated[AsyncIOMotorClient,Depends(get_db)]):
    """
    Handles the forgot password request.
    """
    user = await db["users"].find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # create reset token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    reset_token = create_access_token(
        data={"sub": str(user["_id"])}, expires_delta=access_token_expires
    )

    # send email
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user["email"]],
        body=f"""
        <p>Hi {user['username']},</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>This link will expire in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes.</p>
        """,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Password reset email sent"}

# Reset Password
@router.post(
    "/reset-password", 
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset user password",
    description="Reset the user's password using a valid token."
)
async def reset_password(request: ResetPasswordRequest, db:Annotated[AsyncIOMotorClient,Depends(get_db)]):
    """
    Resets the user's password.
    """
    try:
        payload = jwt.decode(
            request.token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # hash new password
    hashed_password = get_password_hash(request.new_password)

    # update user's password
    await db["users"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}}
    )

    return {"message": "Password has been reset successfully"}
        