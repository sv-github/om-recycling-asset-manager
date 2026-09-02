from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    legal_name: str | None = None
    gstin: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    address: str | None = None
    notes: str | None = None

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Company name cannot be blank.")

        return value


class CustomerUpdate(BaseModel):
    company_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    legal_name: str | None = None
    gstin: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool | None = None

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Company name cannot be blank.")

        return value


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