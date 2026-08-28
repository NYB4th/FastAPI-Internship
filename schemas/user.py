from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["securepassword123"])


class UserResponse(BaseModel):
    id: int = Field(..., examples=[1])
    email: EmailStr = Field(..., examples=["user@example.com"])

    model_config = ConfigDict(from_attributes=True)
