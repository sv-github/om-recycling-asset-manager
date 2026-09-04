from pydantic import BaseModel, Field, field_validator

from app.schemas.asset_inspection import (
    ComponentStatus,
    ConditionStatus,
    InspectionType,
    WorkingStatus,
)


class AssetIntakeItem(BaseModel):
    collection_item_id: int

    serial_number: str | None = None

    @field_validator("serial_number", mode="before")
    @classmethod
    def normalize_serial_number(cls, value):
        if value is None:
            return None

        if isinstance(value, str) and not value.strip():
            return None

        return value

    asset_category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None
    received_by: str | None = None
    receiving_notes: str | None = None
    notes: str | None = None


class AssetIntakeCreate(BaseModel):
    assets: list[AssetIntakeItem] = Field(
        ...,
        min_length=1,
    )


class InitialInspectionIntake(BaseModel):
    inspection_type: InspectionType = InspectionType.INITIAL
    inspected_by: str | None = None

    working_status: WorkingStatus
    overall_condition: ConditionStatus

    display_condition: ConditionStatus
    body_condition: ConditionStatus
    keyboard_condition: ConditionStatus
    touchpad_condition: ConditionStatus
    hinge_condition: ConditionStatus
    ports_condition: ConditionStatus
    battery_condition: ConditionStatus

    charger_status: ComponentStatus
    ram_status: ComponentStatus
    storage_status: ComponentStatus
    cpu_status: ComponentStatus
    gpu_status: ComponentStatus

    accessories: str | None = None
    inspection_notes: str | None = None


class AssetInspectionIntakeItem(BaseModel):
    collection_item_id: int

    serial_number: str | None = None

    @field_validator("serial_number", mode="before")
    @classmethod
    def normalize_serial_number(cls, value):
        if value is None:
            return None

        if isinstance(value, str) and not value.strip():
            return None

        return value

    asset_category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None
    received_by: str | None = None
    receiving_notes: str | None = None
    notes: str | None = None

    inspection: InitialInspectionIntake


class AssetInspectionIntakeCreate(BaseModel):
    assets: list[AssetInspectionIntakeItem] = Field(
        ...,
        min_length=1,
    )