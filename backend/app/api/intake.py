from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_inspection import AssetInspection
from app.models.collection import Collection
from app.models.collection_item import CollectionItem
from app.schemas.asset import AssetResponse
from app.schemas.intake import (
    AssetInspectionIntakeCreate,
    AssetIntakeCreate,
)


router = APIRouter(
    prefix="/api/intake",
    tags=["Collection Receiving / Asset Intake"],
)


@router.post(
    "/collections/{collection_id}",
    response_model=list[AssetResponse],
    status_code=status.HTTP_201_CREATED,
)
def receive_assets(
    collection_id: int,
    intake_data: AssetIntakeCreate,
    db: Session = Depends(get_db),
):
    """
    Receive assets without performing an inspection.
    """

    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    validated_items = []
    serial_numbers = set()

    for item in intake_data.assets:
        collection_item = db.get(
            CollectionItem,
            item.collection_item_id,
        )

        if collection_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Collection item {item.collection_item_id} "
                    "not found."
                ),
            )

        if collection_item.collection_id != collection_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Collection item {item.collection_item_id} "
                    "does not belong to this collection."
                ),
            )

        if item.serial_number:
            if item.serial_number in serial_numbers:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Duplicate serial number in intake request: "
                        f"{item.serial_number}"
                    ),
                )

            serial_numbers.add(item.serial_number)

            existing_asset = db.scalars(
                select(Asset).where(
                    Asset.serial_number == item.serial_number
                )
            ).first()

            if existing_asset is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Serial number already exists: "
                        f"{item.serial_number}"
                    ),
                )

        validated_items.append(item)

    created_assets = []

    try:
        for item in validated_items:
            next_id = db.execute(
                text("SELECT nextval('assets_id_seq')")
            ).scalar_one()

            asset = Asset(
                id=next_id,
                asset_code=f"AST-{next_id:08d}",
                collection_id=collection_id,
                collection_item_id=item.collection_item_id,
                serial_number=item.serial_number,
                asset_category=item.asset_category,
                manufacturer=item.manufacturer,
                model=item.model,
                description=item.description,
                received_by=item.received_by,
                receiving_notes=item.receiving_notes,
                notes=item.notes,
            )

            db.add(asset)
            created_assets.append(asset)

        db.commit()

        for asset in created_assets:
            db.refresh(asset)

    except Exception:
        db.rollback()
        raise

    return created_assets


@router.post(
    "/collections/{collection_id}/with-inspection",
    response_model=list[AssetResponse],
    status_code=status.HTTP_201_CREATED,
)
def receive_assets_with_initial_inspection(
    collection_id: int,
    intake_data: AssetInspectionIntakeCreate,
    db: Session = Depends(get_db),
):
    """
    Receive assets and create their initial inspections
    as one atomic database transaction.
    """

    # ---------------------------------------------------------
    # 1. Verify collection
    # ---------------------------------------------------------

    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    # ---------------------------------------------------------
    # 2. Validate ALL items before creating anything
    # ---------------------------------------------------------

    validated_items = []
    serial_numbers = set()

    for item in intake_data.assets:

        collection_item = db.get(
            CollectionItem,
            item.collection_item_id,
        )

        if collection_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Collection item {item.collection_item_id} "
                    "not found."
                ),
            )

        if collection_item.collection_id != collection_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Collection item {item.collection_item_id} "
                    "does not belong to this collection."
                ),
            )

        # -----------------------------------------------------
        # Duplicate serial number protection
        # -----------------------------------------------------

        if item.serial_number:

            if item.serial_number in serial_numbers:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Duplicate serial number in intake request: "
                        f"{item.serial_number}"
                    ),
                )

            serial_numbers.add(item.serial_number)

            existing_asset = db.scalars(
                select(Asset).where(
                    Asset.serial_number == item.serial_number
                )
            ).first()

            if existing_asset is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Serial number already exists: "
                        f"{item.serial_number}"
                    ),
                )

        validated_items.append(item)

    # ---------------------------------------------------------
    # 3. Create Assets + Initial Inspections
    # ---------------------------------------------------------

    created_assets = []

    try:

        for item in validated_items:

            # Get next PostgreSQL asset ID atomically
            next_id = db.execute(
                text("SELECT nextval('assets_id_seq')")
            ).scalar_one()

            asset = Asset(
                id=next_id,
                asset_code=f"AST-{next_id:08d}",
                collection_id=collection_id,
                collection_item_id=item.collection_item_id,
                serial_number=item.serial_number,
                asset_category=item.asset_category,
                manufacturer=item.manufacturer,
                model=item.model,
                description=item.description,
                received_by=item.received_by,
                receiving_notes=item.receiving_notes,
                notes=item.notes,
            )

            db.add(asset)

            # -------------------------------------------------
            # Create initial inspection for this Asset
            # -------------------------------------------------

            inspection_data = item.inspection.model_dump()

            inspection = AssetInspection(
                asset_id=next_id,
                **inspection_data,
            )

            db.add(inspection)

            created_assets.append(asset)

        # -----------------------------------------------------
        # 4. Commit BOTH Assets and Inspections together
        # -----------------------------------------------------

        db.commit()

        for asset in created_assets:
            db.refresh(asset)

    except Exception:
        db.rollback()
        raise

    return created_assets