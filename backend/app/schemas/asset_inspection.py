from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class InspectionType(str, Enum):
    INITIAL = "initial"
    REFURBISHMENT = "refurbishment"
    FINAL_QC = "final_qc"


class WorkingStatus(str, Enum):
    WORKING = "working"
    NOT_WORKING = "not_working"
    PARTIALLY_WORKING = "partially_working"
    NOT_TESTED = "not_tested"


class ConditionStatus(str, Enum):
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"
    NOT_PRESENT = "not_present"
    NOT_TESTED = "not_tested"
    NOT_APPLICABLE = "not_applicable"


class ComponentStatus(str, Enum):
    PRESENT = "present"
    NOT_PRESENT = "not_present"
    FAULTY = "faulty"
    NOT_TESTED = "not_tested"
    NOT_APPLICABLE = "not_applicable"


class AssetInspectionCreate(BaseModel):
    asset_id: int

    inspection_type: InspectionType = InspectionType.INITIAL

    inspection_date: datetime = None
    inspected_by: str | None = Field(default=None, max_length=150)

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


class AssetInspectionUpdate(BaseModel):
    inspection_type: InspectionType = None

    inspection_date: datetime = None
    inspected_by: str | None = Field(default=None, max_length=150)

    working_status: WorkingStatus = None
    overall_condition: ConditionStatus = None

    display_condition: ConditionStatus = None
    body_condition: ConditionStatus = None
    keyboard_condition: ConditionStatus = None
    touchpad_condition: ConditionStatus = None
    hinge_condition: ConditionStatus = None
    ports_condition: ConditionStatus = None
    battery_condition: ConditionStatus = None
    charger_status: ComponentStatus = None

    ram_status: ComponentStatus = None
    storage_status: ComponentStatus = None
    cpu_status: ComponentStatus = None
    gpu_status: ComponentStatus = None

    accessories: str | None = None
    inspection_notes: str | None = None


class AssetInspectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int

    inspection_type: InspectionType
    inspection_date: datetime
    inspected_by: str | None

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

    accessories: str | None
    inspection_notes: str | None

    created_at: datetime
    updated_at: datetime
