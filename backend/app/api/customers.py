from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)


router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"],
)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = db.scalar(
        select(Customer).where(
            func.lower(Customer.company_name)
            == customer_data.company_name.strip().lower()
        )
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this company name already exists.",
        )

    customer = Customer(
        customer_code="TEMP",
        **customer_data.model_dump(),
    )

    db.add(customer)
    db.flush()

    customer.customer_code = f"CUS-{customer.id:06d}"

    db.commit()
    db.refresh(customer)

    return customer


@router.get(
    "",
    response_model=list[CustomerResponse],
)
def list_customers(
    db: Session = Depends(get_db),
):
    customers = db.scalars(
        select(Customer)
        .order_by(Customer.company_name)
    ).all()

    return customers


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    update_data = customer_data.model_dump(
        exclude_unset=True
    )

    if "company_name" in update_data:
        company_name = update_data["company_name"].strip()

        existing_customer = db.scalar(
            select(Customer).where(
                func.lower(Customer.company_name) == company_name.lower(),
                Customer.id != customer_id,
            )
        )

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this company name already exists.",
            )

        update_data["company_name"] = company_name

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer