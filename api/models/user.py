# user model
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime, timezone
from api.models.pyobjectid import PyObjectId

class User(BaseModel):
    """
    Represents a user in the database.
    """
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    username: str = Field(..., description="Username for the user account")
    email: EmailStr = Field(..., description="Email address for the user account") 
    password: str = Field(..., description="Hashed password for the user account")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the user joined")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "a_very_secret_hash",
                "is_active": True,
            }
        },
    )
