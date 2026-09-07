from datetime import datetime

from pydantic import BaseModel, Field


class AssetReturnCreate(BaseModel):
    disposition_date: datetime | None = None

    processed_by: str | None = Field(
        default=None,
        max_length=150,
    )

    disposition_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    recipient_name: str | None = Field(
        default=None,
        max_length=150,
    )

    recipient_reference: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = None