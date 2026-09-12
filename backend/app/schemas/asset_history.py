from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AssetHistoryEventType = Literal[
    "inspection",
    "processing",
    "sanitization",
    "disposition",
    "return",
]


class AssetHistoryEvent(BaseModel):
    event_type: AssetHistoryEventType
    event_id: int
    event_date: datetime
    title: str
    status: str | None
    details: dict[str, Any] = Field(default_factory=dict)


class AssetHistoryResponse(BaseModel):
    asset_id: int
    asset_code: str
    events: list[AssetHistoryEvent]