from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DispositionType(str, Enum):
    resale = "resale"
    reuse = "reuse"
    internal_use = "internal_use"
    recycling = "recycling"
    scrap = "scrap"
    returned = "returned"
    donated = "donated"
    other = "other"


class DispositionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    completed = "completed"
    cancelled = "cancelled"


class AssetDispositionCreate(BaseModel):
    asset_id: int

    disposition_type: DispositionType

    disposition_date: datetime = None

    processed_by: str | None = Field(default=None, max_length=150)
    disposition_reference: str | None = Field(default=None, max_length=100)
    recipient_name: str | None = Field(default=None, max_length=150)
    recipient_reference: str | None = Field(default=None, max_length=100)

    amount: Decimal | None = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    notes: str | None = None


class AssetDispositionUpdate(BaseModel):
    disposition_type: DispositionType = None

    disposition_date: datetime = None

    processed_by: str | None = Field(default=None, max_length=150)
    disposition_reference: str | None = Field(default=None, max_length=100)
    recipient_name: str | None = Field(default=None, max_length=150)
    recipient_reference: str | None = Field(default=None, max_length=100)

    amount: Decimal | None = Field(
        default=None,
        max_digits=12,
        decimal_places=2,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    notes: str | None = None


class AssetDispositionStatusUpdate(BaseModel):
    disposition_status: DispositionStatus


class AssetDispositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int

    disposition_type: DispositionType
    disposition_status: DispositionStatus

    disposition_date: datetime

    processed_by: str | None
    disposition_reference: str | None

    recipient_name: str | None
    recipient_reference: str | None

    amount: Decimal | None
    currency: str | None

    notes: str | None

    created_at: datetime
    updated_at: datetime
