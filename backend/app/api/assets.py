from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.collection import Collection
from app.models.collection_item import CollectionItem
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
)


router = APIRouter(
    prefix="/api/assets",
    tags=["Assets"],
)


def generate_asset_code(db: Session) -> str:
    last_asset = db.scalars(
        select(Asset)
        .order_by(Asset.id.desc())
    ).first()

    if last_asset is None:
        next_number = 1
    else:
        next_number = last_asset.id + 1

    return f"AST-{next_number:08d}"


@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
):
    # Verify collection
    collection = db.get(Collection, asset_data.collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    # Verify collection item when supplied
    if asset_data.collection_item_id is not None:
        collection_item = db.get(
            CollectionItem,
            asset_data.collection_item_id,
        )

        if collection_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection item not found.",
            )

        # Prevent linking an item belonging to another collection
        if collection_item.collection_id != asset_data.collection_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection item does not belong to the specified collection.",
            )

    asset = Asset(
        asset_code=generate_asset_code(db),
        **asset_data.model_dump(),
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@router.get(
    "",
    response_model=list[AssetResponse],
)
def list_assets(
    collection_id: int | None = None,
    collection_item_id: int | None = None,
    serial_number: str | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Asset)

    if collection_id is not None:
        query = query.where(
            Asset.collection_id == collection_id
        )

    if collection_item_id is not None:
        query = query.where(
            Asset.collection_item_id == collection_item_id
        )

    if serial_number is not None:
        query = query.where(
            Asset.serial_number == serial_number
        )

    if status_filter is not None:
        query = query.where(
            Asset.status == status_filter
        )

    query = query.order_by(Asset.id)

    return db.scalars(query).all()


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    return asset


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
)
def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot modify asset "
                f"with status '{asset.status}'."
            ),
        )

    update_data = asset_data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    return asset