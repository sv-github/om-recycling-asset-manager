from datetime import datetime

from pydantic import BaseModel, Field


class DataSanitizationUpdate(BaseModel):
    data_wipe_status: str = Field(
        ...,
        description=(
            "Sanitization status: not_started, in_progress, "
            "passed, failed"
        ),
    )

    data_wipe_method: str | None = Field(
        default=None,
        max_length=100,
    )

    data_wipe_date: datetime | None = None

    data_wipe_reference: str | None = Field(
        default=None,
        max_length=100,
    )


class DataSanitizationResponse(BaseModel):
    asset_id: int
    asset_code: str

    data_wipe_status: str
    data_wipe_method: str | None
    data_wipe_date: datetime | None
    data_wipe_reference: str | None