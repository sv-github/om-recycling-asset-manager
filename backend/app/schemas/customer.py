from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerCreate(BaseModel):
    company_name: str
    legal_name: str | None = None
    gstin: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    address: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    company_name: str | None = None
    legal_name: str | None = None
    gstin: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_code: str
    company_name: str
    legal_name: str | None
    gstin: str | None
    primary_contact_name: str | None
    primary_contact_email: str | None
    primary_contact_phone: str | None
    address: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime