from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_inspection import AssetInspection
from app.schemas.asset_inspection import (
    AssetInspectionCreate,
    AssetInspectionResponse,
    AssetInspectionUpdate,
)


router = APIRouter(
    prefix="/api/asset-inspections",
    tags=["Asset Inspections"],
)


@router.post(
    "",
    response_model=AssetInspectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset_inspection(
    inspection_data: AssetInspectionCreate,
    db: Session = Depends(get_db),
):
    # Verify that the asset exists
    asset = db.get(Asset, inspection_data.asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot create inspections for an asset "
                f"with status '{asset.status}'."
            ),
        )

    data = inspection_data.model_dump()

    # Let PostgreSQL/server_default provide the current time
    if data.get("inspection_date") is None:
        data.pop("inspection_date", None)

    inspection = AssetInspection(**data)

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    return inspection


@router.get(
    "",
    response_model=list[AssetInspectionResponse],
)
def list_asset_inspections(
    asset_id: int | None = None,
    inspection_type: str | None = None,
    working_status: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(AssetInspection)

    if asset_id is not None:
        query = query.where(
            AssetInspection.asset_id == asset_id
        )

    if inspection_type is not None:
        query = query.where(
            AssetInspection.inspection_type == inspection_type
        )

    if working_status is not None:
        query = query.where(
            AssetInspection.working_status == working_status
        )

    query = query.order_by(
        AssetInspection.inspection_date.desc(),
        AssetInspection.id.desc(),
    )

    return db.scalars(query).all()


@router.get(
    "/{inspection_id}",
    response_model=AssetInspectionResponse,
)
def get_asset_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
):
    inspection = db.get(
        AssetInspection,
        inspection_id,
    )

    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset inspection not found.",
        )

    return inspection


@router.put(
    "/{inspection_id}",
    response_model=AssetInspectionResponse,
)
def update_asset_inspection(
    inspection_id: int,
    inspection_data: AssetInspectionUpdate,
    db: Session = Depends(get_db),
):
    inspection = db.get(
        AssetInspection,
        inspection_id,
    )

    if inspection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset inspection not found.",
        )

    asset = db.get(Asset, inspection.asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot modify inspections for an asset "
                f"with status '{asset.status}'."
            ),
        )

    update_data = inspection_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(inspection, field, value)

    db.commit()
    db.refresh(inspection)

    return inspection
