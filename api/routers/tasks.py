# tasks router
from fastapi import APIRouter, Depends, HTTPException, status
from api.dependencies.database import get_db
from api.models.task import Task
from api.models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated
from datetime import datetime, timezone
from bson import ObjectId

from api.dependencies.auth import get_current_user
from api.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_user)]
)

# Create Task
@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the currently authenticated user."
)
async def create_task(
    task:TaskCreate, 
    db:Annotated[AsyncIOMotorDatabase,Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    task_data = task.model_dump()
    task_data["user_id"] = str(current_user.id)
    task_data["created_at"] = datetime.now(timezone.utc)
    task_data["updated_at"] = datetime.now(timezone.utc)
    task_data["is_completed"] = task.is_completed or False
    
    result = await db["tasks"].insert_one(task_data)
    new_task = await db["tasks"].find_one({"_id":result.inserted_id})

    return new_task

# Get All Tasks
@router.get(
    "",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks",
    description="Get all tasks for the currently authenticated user."
)
async def get_tasks(
    db:Annotated[AsyncIOMotorDatabase,Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    tasks = await db["tasks"].find({"user_id": str(current_user.id)}).to_list(length=None)
    return tasks

# Get Task by ID
@router.get(
    "/{task_id}", 
    response_model=TaskResponse, 
    status_code=status.HTTP_200_OK,
    summary="Get a single task by ID",
    description="Get a single task by its ID. The task must belong to the currently authenticated user."
)
async def get_task(
    task_id:str, 
    db:Annotated[AsyncIOMotorDatabase,Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    task = await db["tasks"].find_one({"_id":ObjectId(task_id), "user_id":str(current_user.id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

# update task
@router.put(
    "/{task_id}", 
    response_model=TaskResponse, 
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Update a task by its ID. The task must belong to the currently authenticated user."
)
async def update_task(
    task_id:str, 
    task:TaskUpdate, 
    db:Annotated[AsyncIOMotorDatabase,Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    update_data = task.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db["tasks"].update_one(
        {"_id":ObjectId(task_id), "user_id":str(current_user.id)},
        {"$set":update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated_task = await db["tasks"].find_one({"_id":ObjectId(task_id)})
    return updated_task

# delete task
@router.delete(
    "/{task_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by its ID. The task must belong to the currently authenticated user."
)
async def delete_task(
    task_id:str, 
    db:Annotated[AsyncIOMotorDatabase,Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    result = await db["tasks"].delete_one({"_id":ObjectId(task_id), "user_id":str(current_user.id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return