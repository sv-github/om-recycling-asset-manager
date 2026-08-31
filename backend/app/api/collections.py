from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection import Collection
from app.models.customer import Customer
from app.models.customer_location import CustomerLocation
from app.schemas.collection import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
)


router = APIRouter(
    prefix="/api/collections",
    tags=["Collections"],
)


@router.post(
    "",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_collection(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, collection_data.customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    location = db.get(
        CustomerLocation,
        collection_data.location_id,
    )

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer location not found.",
        )

    if location.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer location does not belong to the selected customer.",
        )

    if collection_data.expected_item_count is not None:
        if collection_data.expected_item_count < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expected item count cannot be negative.",
            )

    collection = Collection(
        collection_code="TEMP",
        **collection_data.model_dump(),
    )

    db.add(collection)
    db.flush()

    collection.collection_code = f"COL-{collection.id:06d}"

    db.commit()
    db.refresh(collection)

    return collection


@router.get(
    "",
    response_model=list[CollectionResponse],
)
def list_collections(
    customer_id: int | None = None,
    location_id: int | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Collection)

    if customer_id is not None:
        query = query.where(
            Collection.customer_id == customer_id
        )

    if location_id is not None:
        query = query.where(
            Collection.location_id == location_id
        )

    if status_filter is not None:
        query = query.where(
            Collection.status == status_filter
        )

    query = query.order_by(
        Collection.collection_date.desc(),
        Collection.id.desc(),
    )

    return db.scalars(query).all()


@router.get(
    "/{collection_id}",
    response_model=CollectionResponse,
)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
):
    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    return collection


@router.put(
    "/{collection_id}",
    response_model=CollectionResponse,
)
def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db),
):
    collection = db.get(Collection, collection_id)

    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found.",
        )

    update_data = collection_data.model_dump(
        exclude_unset=True
    )

    if "pickup_receipt_number" in update_data:
        receipt_number = update_data["pickup_receipt_number"]

        if receipt_number:
            existing = db.scalar(
                select(Collection).where(
                    Collection.pickup_receipt_number == receipt_number,
                    Collection.id != collection.id,
                )
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Pickup receipt number already exists.",
                )

    for field, value in update_data.items():
        setattr(collection, field, value)

    db.commit()
    db.refresh(collection)

    return collection