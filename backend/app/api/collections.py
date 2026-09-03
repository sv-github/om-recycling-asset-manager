from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection import Collection
from app.models.collection_status import CollectionStatus
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

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer is inactive.",
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

    if not location.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer location is inactive.",
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

    collection_status = db.scalar(
        select(CollectionStatus).where(
            CollectionStatus.code == collection_data.status,
            CollectionStatus.is_active.is_(True),
        )
    )

    if collection_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection status does not exist or is inactive.",
        )

    collection = Collection(
        collection_code="TEMP",
        customer_id=collection_data.customer_id,
        location_id=collection_data.location_id,
        collection_date=collection_data.collection_date,
        pickup_receipt_number=collection_data.pickup_receipt_number,
        source_type=collection_data.source_type,
        status_id=collection_status.id,
        expected_item_count=collection_data.expected_item_count,
        transport_reference=collection_data.transport_reference,
        notes=collection_data.notes,
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
        query = query.join(
            CollectionStatus,
            Collection.status_id == CollectionStatus.id,
        ).where(
            CollectionStatus.code == status_filter
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

    if (
        "expected_item_count" in update_data
        and update_data["expected_item_count"] is not None
        and update_data["expected_item_count"] < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expected_item_count cannot be negative.",
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

    if "status" in update_data:
        collection_status = db.scalar(
            select(CollectionStatus).where(
                CollectionStatus.code == update_data["status"],
                CollectionStatus.is_active.is_(True),
            )
        )

        if collection_status is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection status does not exist or is inactive.",
            )

        collection.status_id = collection_status.id
        del update_data["status"]

    for field, value in update_data.items():
        setattr(collection, field, value)

    db.commit()
    db.refresh(collection)

    return collection