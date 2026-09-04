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

router = APIRouter(prefix="/api/customer-locations", tags=["Customer Locations"])


@router.post(
    "",
    response_model=CustomerLocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_location(
    data: CustomerLocationCreate,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, data.customer_id)

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

    location = CustomerLocation(
        location_code="TEMP",
        customer_id=data.customer_id,
        location_name=data.location_name,
        address=data.address,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        notes=data.notes,
    )

    db.add(location)
    db.flush()

    location.location_code = f"LOC-{location.id:06d}"

    db.commit()
    db.refresh(location)

    return location


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


@router.get(
    "/customer/{customer_id}",
    response_model=list[CustomerLocationResponse],
)
def list_customer_locations(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return db.scalars(
        select(CustomerLocation)
        .where(CustomerLocation.customer_id == customer_id)
        .order_by(CustomerLocation.id)
    ).all()


@router.put(
    "/{location_id}",
    response_model=CustomerLocationResponse,
)
def update_customer_location(
    location_id: int,
    data: CustomerLocationUpdate,
    db: Session = Depends(get_db),
):
    location = db.get(CustomerLocation, location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer location not found.",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return location