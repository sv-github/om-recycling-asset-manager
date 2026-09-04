from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CollectionStatusCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    sort_order: int
    is_active: bool = True


class CollectionStatusUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    sort_order: int = None
    is_active: bool = None


class CollectionStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime