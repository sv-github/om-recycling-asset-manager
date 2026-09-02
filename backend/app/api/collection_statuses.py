from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.collection_status import CollectionStatus
from app.schemas.collection_status import (
    CollectionStatusCreate,
    CollectionStatusResponse,
    CollectionStatusUpdate,
)


router = APIRouter(
    prefix="/api/collection-statuses",
    tags=["Collection Statuses"],
)


@router.post(
    "",
    response_model=CollectionStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_collection_status(
    status_data: CollectionStatusCreate,
    db: Session = Depends(get_db),
):
    code = status_data.code.strip().lower()
    name = status_data.name.strip()

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status code cannot be empty.",
        )

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status name cannot be empty.",
        )

    existing_status = db.scalar(
        select(CollectionStatus).where(
            CollectionStatus.code == code
        )
    )

    if existing_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A collection status with this code already exists.",
        )

    collection_status = CollectionStatus(
        code=code,
        name=name,
        description=status_data.description,
        sort_order=status_data.sort_order,
        is_active=status_data.is_active,
    )

    db.add(collection_status)
    db.commit()
    db.refresh(collection_status)

    return collection_status


@router.get(
    "",
    response_model=list[CollectionStatusResponse],
)
def list_collection_statuses(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = select(CollectionStatus)

    if not include_inactive:
        query = query.where(
            CollectionStatus.is_active.is_(True)
        )

    query = query.order_by(
        CollectionStatus.sort_order,
        CollectionStatus.id,
    )

    return db.scalars(query).all()


@router.get(
    "/{status_id}",
    response_model=CollectionStatusResponse,
)
def get_collection_status(
    status_id: int,
    db: Session = Depends(get_db),
):
    collection_status = db.get(
        CollectionStatus,
        status_id,
    )

    if collection_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection status not found.",
        )

    return collection_status


@router.put(
    "/{status_id}",
    response_model=CollectionStatusResponse,
)
def update_collection_status(
    status_id: int,
    status_data: CollectionStatusUpdate,
    db: Session = Depends(get_db),
):
    collection_status = db.get(
        CollectionStatus,
        status_id,
    )

    if collection_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection status not found.",
        )

    update_data = status_data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        name = update_data["name"].strip()

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status name cannot be empty.",
            )

        update_data["name"] = name

    for field, value in update_data.items():
        setattr(collection_status, field, value)

    db.commit()
    db.refresh(collection_status)

    return collection_status