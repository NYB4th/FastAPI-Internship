from pydantic import BaseModel, Field
from typing import Literal


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title can not be empty")
    description: str
    priority: int = Field(
        ..., ge=1, le=5, description="Priority must be between 1 and 5"
    )
    status: Literal["pending", "in_progress", "completed"] = "pending"


class TaskRead(TaskCreate):
    id: int
