from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.customer_location import CustomerLocation
from app.schemas.customer_location import (
    CustomerLocationCreate,
    CustomerLocationResponse,
    CustomerLocationUpdate,
)


router = APIRouter(
    prefix="/api/customer-locations",
    tags=["Customer Locations"],
)


@router.post(
    "",
    response_model=CustomerLocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_location(
    location_data: CustomerLocationCreate,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, location_data.customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    location = CustomerLocation(
        location_code="TEMP",
        **location_data.model_dump(),
    )

    db.add(location)
    db.flush()

    location.location_code = f"LOC-{location.id:06d}"

    db.commit()
    db.refresh(location)

    return location


@router.get(
    "",
    response_model=list[CustomerLocationResponse],
)
def list_customer_locations(
    customer_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = select(CustomerLocation)

    if customer_id is not None:
        query = query.where(
            CustomerLocation.customer_id == customer_id
        )

    query = query.order_by(CustomerLocation.location_name)

    return db.scalars(query).all()


@router.get(
    "/{location_id}",
    response_model=CustomerLocationResponse,
)
def get_customer_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    location = db.get(CustomerLocation, location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer location not found.",
        )

    return location


@router.put(
    "/{location_id}",
    response_model=CustomerLocationResponse,
)
def update_customer_location(
    location_id: int,
    location_data: CustomerLocationUpdate,
    db: Session = Depends(get_db),
):
    location = db.get(CustomerLocation, location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer location not found.",
        )

    update_data = location_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return location