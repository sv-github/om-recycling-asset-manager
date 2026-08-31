from pydantic import BaseModel, Field

from app.schemas.asset_inspection import (
    InspectionType,
    WorkingStatus,
    ConditionStatus,
    ComponentStatus,
)


class AssetIntakeItem(BaseModel):
    """
    Asset-only intake item.

    Used by:
        POST /api/intake/collections/{collection_id}
    """

    collection_item_id: int

    serial_number: str | None = None

    asset_category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None

    received_by: str | None = None
    receiving_notes: str | None = None
    notes: str | None = None


class AssetIntakeCreate(BaseModel):
    """
    Request for receiving one or more assets
    without performing an inspection.
    """

    assets: list[AssetIntakeItem] = Field(
        min_length=1,
        description="One entry for each physical asset received.",
    )


class InitialInspectionIntake(BaseModel):
    """
    Initial inspection information collected
    at the time an asset is received.

    asset_id is intentionally NOT included because
    the Asset has not yet been created. The intake
    workflow will create the Asset first and then
    attach this inspection to it.
    """

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
    """
    One physical asset received together with
    its initial inspection.
    """

    collection_item_id: int

    serial_number: str | None = None

    asset_category: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None

    received_by: str | None = None
    receiving_notes: str | None = None
    notes: str | None = None

    inspection: InitialInspectionIntake


class AssetInspectionIntakeCreate(BaseModel):
    """
    Request for receiving one or more assets
    and performing their initial inspections
    as one transaction.
    """

    assets: list[AssetInspectionIntakeItem] = Field(
        min_length=1,
        description="Assets received and inspected during intake.",
    )