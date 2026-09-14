from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset_category import AssetCategory
from app.schemas.asset_category import (
    AssetCategoryCreate,
    AssetCategoryResponse,
    AssetCategoryUpdate,
)


router = APIRouter(
    prefix="/api/asset-categories",
    tags=["Asset Categories"],
)


def _normalize_code(value: str) -> str:
    return value.strip().upper()


def _normalize_name(value: str) -> str:
    return value.strip()


@router.post(
    "",
    response_model=AssetCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset_category(
    category_data: AssetCategoryCreate,
    db: Session = Depends(get_db),
):
    code = _normalize_code(category_data.code)
    name = _normalize_name(category_data.name)

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category code cannot be empty.",
        )

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty.",
        )

    existing_category = db.scalar(
        select(AssetCategory).where(
            func.lower(AssetCategory.code) == code.lower()
        )
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An asset category with this code already exists.",
        )

    existing_name = db.scalar(
        select(AssetCategory).where(
            func.lower(AssetCategory.name) == name.lower()
        )
    )

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An asset category with this name already exists.",
        )

    category = AssetCategory(
        code=code,
        name=name,
        description=category_data.description,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active,
    )

    db.add(category)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create the asset category because it conflicts "
                "with an existing category."
            ),
        )

    db.refresh(category)
    return category


@router.get(
    "",
    response_model=list[AssetCategoryResponse],
)
def list_asset_categories(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = select(AssetCategory)

    if not include_inactive:
        query = query.where(AssetCategory.is_active.is_(True))

    query = query.order_by(
        AssetCategory.sort_order,
        AssetCategory.id,
    )

    return db.scalars(query).all()


@router.get(
    "/{category_id}",
    response_model=AssetCategoryResponse,
)
def get_asset_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.get(AssetCategory, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset category not found.",
        )

    return category


@router.put(
    "/{category_id}",
    response_model=AssetCategoryResponse,
)
def update_asset_category(
    category_id: int,
    category_data: AssetCategoryUpdate,
    db: Session = Depends(get_db),
):
    category = db.get(AssetCategory, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset category not found.",
        )

    update_data = category_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        name = _normalize_name(update_data["name"])

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty.",
            )

        existing_name = db.scalar(
            select(AssetCategory).where(
                func.lower(AssetCategory.name) == name.lower(),
                AssetCategory.id != category_id,
            )
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An asset category with this name already exists.",
            )

        update_data["name"] = name

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update the asset category.",
        )

    db.refresh(category)
    return category
