# task schemas
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

from api.models.user import PyObjectId


class TaskBase(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=300)
    due_date: Optional[datetime] = None
    category: Optional[str] = None
    is_completed: bool = False


class TaskCreate(TaskBase):
    title: str = Field(..., min_length=3, max_length=50)


class TaskUpdate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: PyObjectId = Field(validation_alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
