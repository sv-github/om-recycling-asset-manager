from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerLocationCreate(BaseModel):
    customer_id: int
    location_name: str
    address: str | None = None
    contact_name: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    notes: str | None = None


class CustomerLocationUpdate(BaseModel):
    location_name: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_email: EmailStr | None = None
    contact_phone: str | None = None
    notes: str | None = None
    is_active: bool | None = None


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