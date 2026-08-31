from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AssetProcessingCreate(BaseModel):
    asset_id: int

    processing_type: str = Field(
        ...,
        description=(
            "grading, refurbishment, or "
            "grading_and_refurbishment"
        ),
    )

    grade: str | None = Field(
        default=None,
        description="A, B, C, D, or SCRAP",
    )

    refurbishment_status: str = Field(
        default="not_required",
        description=(
            "not_required, pending, in_progress, "
            "completed, or failed"
        ),
    )

    processor: str | None = Field(
        default=None,
        max_length=150,
    )

    processing_date: datetime | None = None

    condition_summary: str | None = None

    repairs_performed: str | None = None

    parts_replaced: str | None = None

    testing_notes: str | None = None

    processing_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    notes: str | None = None


class AssetProcessingUpdate(BaseModel):
    processing_type: str | None = None

    grade: str | None = None

    refurbishment_status: str | None = None

    processor: str | None = Field(
        default=None,
        max_length=150,
    )

    processing_date: datetime | None = None

    condition_summary: str | None = None

    repairs_performed: str | None = None

    parts_replaced: str | None = None

    testing_notes: str | None = None

    processing_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    notes: str | None = None


class AssetProcessingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int

    processing_type: str
    grade: str | None

    refurbishment_status: str

    processor: str | None

    processing_date: datetime

    condition_summary: str | None

    repairs_performed: str | None

    parts_replaced: str | None

    testing_notes: str | None

    processing_reference: str | None

    cost: Decimal | None

    notes: str | None

    created_at: datetime
    updated_at: datetime