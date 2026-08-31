from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CollectionItemCreate(BaseModel):
    collection_id: int
    category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None
    expected_quantity: int
    notes: str | None = None


class CollectionItemUpdate(BaseModel):
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None
    expected_quantity: int | None = None
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