from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        description="Task title can not be empty",
        examples=["Complete API Documentation"],
    )
    description: str | None = Field(
        None, examples=["Add Pydantic schema examples for OpenAPI"]
    )
    priority: int = Field(
        ...,
        ge=1,
        le=5,
        description="Priority must be between 1 and 5",
        examples=[1],
    )
    status: Literal["pending", "in_progress", "completed"] = Field(
        "pending", examples=["pending"]
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(
        None,
        min_length=1,
        description="Task title can not be empty",
        examples=["Updated Task Title"],
    )
    description: str | None = Field(None, examples=["Updated task description details"])
    priority: int | None = Field(
        None,
        ge=1,
        le=5,
        description="Priority must be between 1 and 5",
        examples=[2],
    )
    status: Literal["pending", "in_progress", "completed"] | None = Field(
        None, examples=["in_progress"]
    )


class TaskRead(TaskCreate):
    id: int = Field(..., examples=[1])
    model_config = ConfigDict(from_attributes=True)
