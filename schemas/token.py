from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(
        ..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sample_token_payload"]
    )
    token_type: str = Field(..., examples=["bearer"])


class TokenData(BaseModel):
    email: str | None = Field(None, examples=["user@example.com"])
