from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CollectionItemCreate(BaseModel):
    collection_id: int
    category: str = Field(max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=150)
    description: str | None = None
    expected_quantity: int = Field(gt=0)
    notes: str | None = None


class CollectionItemUpdate(BaseModel):
    category: str = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=150)
    description: str | None = None
    expected_quantity: int = Field(default=None, gt=0)
    notes: str | None = None


class CollectionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_id: int
    category: str
    manufacturer: str | None
    model: str | None
    description: str | None
    expected_quantity: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
