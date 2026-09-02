from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetCreate(BaseModel):
    collection_id: int
    collection_item_id: int | None = None

    serial_number: str | None = None

    asset_category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None

    received_by: str | None = None
    receiving_notes: str | None = None

    notes: str | None = None


class AssetUpdate(BaseModel):
    serial_number: str | None = None

    asset_category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None

    received_by: str | None = None
    receiving_notes: str | None = None

    notes: str | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_code: str
    serial_number: str | None

    collection_id: int
    collection_item_id: int | None

    asset_category: str
    manufacturer: str | None
    model: str | None
    description: str | None

    status: str

    received_at: datetime
    received_by: str | None
    receiving_notes: str | None

    data_wipe_status: str
    data_wipe_method: str | None
    data_wipe_date: datetime | None
    data_wipe_reference: str | None

    final_disposition: str | None
    notes: str | None

    created_at: datetime
    updated_at: datetime