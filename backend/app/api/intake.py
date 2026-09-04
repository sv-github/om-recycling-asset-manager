from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
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
    tags=["Asset Intake"],
)


def _validate_collection_item(
    db: Session,
    collection_id: int,
    collection_item_id: int,
) -> CollectionItem:
    item = db.get(CollectionItem, collection_item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection item {collection_item_id} not found.",
        )

    if item.collection_id != collection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Collection item {collection_item_id} does not belong "
                f"to collection {collection_id}."
            ),
        )

    return item


def _check_duplicate_serial(
    db: Session,
    serial_number: str,
    serial_keys: set[str],
) -> None:
    serial_key = serial_number.lower()

    if serial_key in serial_keys:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Duplicate serial number in intake request: "
                f"{serial_number}"
            ),
        )

    serial_keys.add(serial_key)

    existing_asset = db.scalars(
        select(Asset).where(
            func.lower(Asset.serial_number) == func.lower(serial_number)
        )
    ).first()

    if existing_asset is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Serial number already exists: {serial_number}",
        )


@router.post(
    "/collections/{collection_id}",
    response_model=list[AssetResponse],
    status_code=status.HTTP_201_CREATED,
)
def receive_assets(
    collection_id: int,
    data: AssetIntakeCreate,
    db: Session = Depends(get_db),
):
    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    serial_keys: set[str] = set()
    created_assets: list[Asset] = []

    try:
        for item in data.assets:
            collection_item = _validate_collection_item(
                db,
                collection_id,
                item.collection_item_id,
            )

            if item.serial_number is not None:
                _check_duplicate_serial(
                    db,
                    item.serial_number,
                    serial_keys,
                )

            asset = Asset(
                asset_code="TEMP",
                serial_number=item.serial_number,
                collection_id=collection_id,
                collection_item_id=collection_item.id,
                asset_category=item.asset_category,
                manufacturer=item.manufacturer,
                model=item.model,
                description=item.description,
                received_by=item.received_by,
                receiving_notes=item.receiving_notes,
                notes=item.notes,
            )

            db.add(asset)
            db.flush()

            asset.asset_code = f"AST-{asset.id:08d}"

            created_assets.append(asset)

        db.commit()

        for asset in created_assets:
            db.refresh(asset)

    except IntegrityError as exc:
        db.rollback()

        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        if constraint_name == "uq_assets_serial_number_not_null":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Serial number already exists.",
            ) from exc

        raise

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
    data: AssetInspectionIntakeCreate,
    db: Session = Depends(get_db),
):
    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    serial_keys: set[str] = set()
    created_assets: list[Asset] = []

    try:
        for item in data.assets:
            collection_item = _validate_collection_item(
                db,
                collection_id,
                item.collection_item_id,
            )

            if item.serial_number is not None:
                _check_duplicate_serial(
                    db,
                    item.serial_number,
                    serial_keys,
                )

            asset = Asset(
                asset_code="TEMP",
                serial_number=item.serial_number,
                collection_id=collection_id,
                collection_item_id=collection_item.id,
                asset_category=item.asset_category,
                manufacturer=item.manufacturer,
                model=item.model,
                description=item.description,
                received_by=item.received_by,
                receiving_notes=item.receiving_notes,
                notes=item.notes,
            )

            db.add(asset)
            db.flush()

            asset.asset_code = f"AST-{asset.id:08d}"

            inspection_data = item.inspection

            inspection = AssetInspection(
                asset_id=asset.id,
                inspection_type=inspection_data.inspection_type,
                inspected_by=inspection_data.inspected_by,
                working_status=inspection_data.working_status,
                overall_condition=inspection_data.overall_condition,
                display_condition=inspection_data.display_condition,
                body_condition=inspection_data.body_condition,
                keyboard_condition=inspection_data.keyboard_condition,
                touchpad_condition=inspection_data.touchpad_condition,
                hinge_condition=inspection_data.hinge_condition,
                ports_condition=inspection_data.ports_condition,
                battery_condition=inspection_data.battery_condition,
                charger_status=inspection_data.charger_status,
                ram_status=inspection_data.ram_status,
                storage_status=inspection_data.storage_status,
                cpu_status=inspection_data.cpu_status,
                gpu_status=inspection_data.gpu_status,
                accessories=inspection_data.accessories,
                inspection_notes=inspection_data.inspection_notes,
            )

            db.add(inspection)
            created_assets.append(asset)

        db.commit()

        for asset in created_assets:
            db.refresh(asset)

    except IntegrityError as exc:
        db.rollback()

        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        if constraint_name == "uq_assets_serial_number_not_null":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Serial number already exists.",
            ) from exc

        raise

    except Exception:
        db.rollback()
        raise

    return created_assets