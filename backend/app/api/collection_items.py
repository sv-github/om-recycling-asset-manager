from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection import Collection
from app.models.collection_item import CollectionItem
from app.schemas.collection_item import (
    CollectionItemCreate,
    CollectionItemResponse,
    CollectionItemUpdate,
)


router = APIRouter(
    prefix="/api/collection-items",
    tags=["Collection Items"],
)


@router.post(
    "",
    response_model=CollectionItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_collection_item(
    item_data: CollectionItemCreate,
    db: Session = Depends(get_db),
):
    collection = db.get(Collection, item_data.collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    if item_data.expected_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expected quantity must be greater than zero.",
        )

    item = CollectionItem(
        **item_data.model_dump()
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get(
    "",
    response_model=list[CollectionItemResponse],
)
def list_collection_items(
    collection_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(CollectionItem)

    if collection_id is not None:
        query = query.where(
            CollectionItem.collection_id == collection_id
        )

    query = query.order_by(CollectionItem.id)

    return db.scalars(query).all()


@router.get(
    "/{item_id}",
    response_model=CollectionItemResponse,
)
def get_collection_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = db.get(CollectionItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection item not found.",
        )

    return item


@router.put(
    "/{item_id}",
    response_model=CollectionItemResponse,
)
def update_collection_item(
    item_id: int,
    item_data: CollectionItemUpdate,
    db: Session = Depends(get_db),
):
    item = db.get(CollectionItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection item not found.",
        )

    update_data = item_data.model_dump(
        exclude_unset=True
    )

    if "expected_quantity" in update_data:
        if update_data["expected_quantity"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expected quantity must be greater than zero.",
            )

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return item