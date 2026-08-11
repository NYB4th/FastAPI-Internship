from pydantic import BaseModel, Field


class ItemRead(BaseModel):
    id: int = Field(..., gt=0, description="the item must have an id")
    name: str = Field(..., min_length=2, description="the item must have a name")
    price: float = Field(..., gt=0, description="the item must have a price")
