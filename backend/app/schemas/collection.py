from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CollectionCreate(BaseModel):
    customer_id: int
    location_id: int
    collection_date: date
    pickup_receipt_number: str | None = Field(default=None, max_length=50)
    source_type: str = Field(max_length=30)
    status: str = "scheduled"
    expected_item_count: int | None = Field(default=None, ge=0)
    transport_reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class CollectionUpdate(BaseModel):
    collection_date: date = None
    pickup_receipt_number: str | None = Field(default=None, max_length=50)
    source_type: str = Field(default=None, max_length=30)
    status: str = None
    expected_item_count: int | None = Field(default=None, ge=0)
    transport_reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    is_active: bool = None


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    collection_code: str
    customer_id: int
    location_id: int
    collection_date: date
    pickup_receipt_number: str | None
    source_type: str
    status: str
    expected_item_count: int | None
    transport_reference: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def serialize_status(cls, value):
        if hasattr(value, "code"):
            return value.code

        return value
