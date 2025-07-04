# task model
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, ClassVar
from datetime import datetime, timezone
import uuid

class Task(BaseModel):
    """
    Represents a task in the database.
    """
    id: Optional[str] = Field(alias='_id', default=str(uuid.uuid4()))
    title: str = Field(..., description="Title of the task", min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, description="Optional description of the task", max_length=300)
    is_completed: bool = Field(default=False, description="Whether the task is completed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the task was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When the task was last updated")
    user_id: str = Field(..., description="ID of the user who owns this task")
    due_date: Optional[datetime] = Field(default=None, description="Optional due date for the task")
    category: Optional[str] = Field(default=None, description="Optional category for the task")
    # Define valid categories as a class variable
    VALID_CATEGORIES: ClassVar[list[str]] = [
        "work",
        "hobbies", 
        "education",
        "savings",
        "health",
        "family",
        "personal",
        "shopping",
        "travel",
        "other"
    ]

    @field_validator("category")
    def validate_category(cls, v):
        if v is not None and v.lower() not in cls.VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(cls.VALID_CATEGORIES)}")
        return v.lower() if v else None

    model_config = ConfigDict(
        # populate_by_name=True allows the model to be populated using either alias names or field names
        # e.g. both '_id' and 'id' will work when creating a Task instance
        populate_by_name=True,
        
        # from_attributes=True enables the model to be created from objects with attributes
        # This is useful when working with ORMs or when converting database models to Pydantic models
        from_attributes=True,
        
        json_schema_extra={
            "example": {
                "title": "Finish the project report",
                "description": "Complete all sections of the quarterly report.", 
                "is_completed": False,
                "user_id": "user_123",
                "due_date": "2024-08-15T23:59:59Z",
                "category": "Work"
            }
        },
    )
