from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["securepassword123"])


class UserResponse(BaseModel):
    id: int = Field(..., examples=[1])
    email: EmailStr = Field(..., examples=["user@example.com"])
    role: Literal["user", "admin"] = Field(default="user", examples=["user"])

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"] = Field(..., examples=["admin"])
