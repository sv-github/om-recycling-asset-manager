from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerLocationCreate(BaseModel):
    customer_id: int
    location_name: str = Field(max_length=150)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=150)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = None


class CustomerLocationUpdate(BaseModel):
    location_name: str = Field(default=None, max_length=150)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=150)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    notes: str | None = None
    is_active: bool = None


class CustomerLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    location_code: str
    location_name: str
    address: str | None
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
