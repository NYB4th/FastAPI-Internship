from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title can not be empty")
    description: str | None = None
    priority: int = Field(
        ..., ge=1, le=5, description="Priority must be between 1 and 5"
    )
    status: Literal["pending", "in_progress", "completed"] = "pending"


class TaskUpdate(BaseModel):
    title: str | None = Field(
        None, min_length=1, description="Task title can not be empty"
    )
    description: str | None = None
    prioirity: int | None = Field(
        None, ge=1, le=5, description="Priority must be between 1 and 5"
    )
    status: Literal["pending", "in_progress", "completed"] | None = None


class TaskRead(TaskCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
