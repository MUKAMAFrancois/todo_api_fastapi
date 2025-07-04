# user schemas
from datetime import datetime
from bson import ObjectId
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ConfigDict,
)
import re

from api.models.user import PyObjectId


class UserBase(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserCreate(BaseModel):
    email: EmailStr = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="User's email address",
    )
    password: str = Field(..., min_length=8, description="User's password")

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="User's username (alphanumeric and underscores only)",
    )

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#_\-^])[A-Za-z\d@$!%*?&#_\-^]{8,}$",
            v,
        ):
            raise ValueError(
                "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character"
            )
        return v

    @field_validator("email")
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Invalid email address")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: PyObjectId = Field(validation_alias="_id")
    email: EmailStr
    username: str
    joined_at: datetime
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class UserSignupResponse(BaseModel):
    id: PyObjectId = Field(validation_alias="_id")
    email: EmailStr
    username: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class Token(BaseModel):
    message: str
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ResetPasswordResponse(BaseModel):
    message: str