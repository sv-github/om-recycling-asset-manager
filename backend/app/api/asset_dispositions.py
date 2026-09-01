from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_disposition import AssetDisposition
from app.schemas.asset_disposition import (
    AssetDispositionCreate,
    AssetDispositionResponse,
    AssetDispositionStatusUpdate,
    AssetDispositionUpdate,
    DispositionStatus,
    DispositionType,
)


router = APIRouter(
    prefix="/api/asset-dispositions",
    tags=["ASSET DISPOSITIONS"],
)


REUSE_DISPOSITIONS = {
    DispositionType.resale,
    DispositionType.reuse,
    DispositionType.internal_use,
    DispositionType.donated,
}


ALLOWED_STATUS_TRANSITIONS = {
    DispositionStatus.pending: {
        DispositionStatus.approved,
        DispositionStatus.cancelled,
    },
    DispositionStatus.approved: {
        DispositionStatus.completed,
        DispositionStatus.cancelled,
    },
    DispositionStatus.completed: set(),
    DispositionStatus.cancelled: set(),
}


def get_asset_or_404(
    asset_id: int,
    db: Session,
) -> Asset:
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} not found",
        )

    return asset


def get_disposition_or_404(
    disposition_id: int,
    db: Session,
) -> AssetDisposition:
    disposition = db.get(
        AssetDisposition,
        disposition_id,
    )

    if disposition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset disposition {disposition_id} not found",
        )

    return disposition


@router.post(
    "",
    response_model=AssetDispositionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset_disposition(
    payload: AssetDispositionCreate,
    db: Session = Depends(get_db),
):
    asset = get_asset_or_404(
        payload.asset_id,
        db,
    )

    existing_completed = db.scalar(
        select(AssetDisposition)
        .where(
            AssetDisposition.asset_id == payload.asset_id,
            AssetDisposition.disposition_status
            == DispositionStatus.completed.value,
        )
        .limit(1)
    )

    if existing_completed is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Asset {payload.asset_id} already has a "
                "completed disposition"
            ),
        )

    if asset.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Asset {payload.asset_id} is already closed "
                "and cannot receive a new disposition"
            ),
        )

    disposition = AssetDisposition(
        asset_id=payload.asset_id,
        disposition_type=payload.disposition_type.value,
        disposition_date=payload.disposition_date,
        processed_by=payload.processed_by,
        disposition_reference=payload.disposition_reference,
        recipient_name=payload.recipient_name,
        recipient_reference=payload.recipient_reference,
        amount=payload.amount,
        currency=payload.currency,
        notes=payload.notes,
    )

    db.add(disposition)

    db.commit()
    db.refresh(disposition)

    return disposition


@router.get(
    "/{disposition_id}",
    response_model=AssetDispositionResponse,
)
def get_asset_disposition(
    disposition_id: int,
    db: Session = Depends(get_db),
):
    return get_disposition_or_404(
        disposition_id,
        db,
    )


@router.get(
    "/asset/{asset_id}",
    response_model=list[AssetDispositionResponse],
)
def list_asset_dispositions(
    asset_id: int,
    db: Session = Depends(get_db),
):
    get_asset_or_404(
        asset_id,
        db,
    )

    dispositions = db.scalars(
        select(AssetDisposition)
        .where(
            AssetDisposition.asset_id == asset_id,
        )
        .order_by(
            AssetDisposition.disposition_date.desc(),
            AssetDisposition.id.desc(),
        )
    ).all()

    return dispositions


@router.patch(
    "/{disposition_id}",
    response_model=AssetDispositionResponse,
)
def update_asset_disposition(
    disposition_id: int,
    payload: AssetDispositionUpdate,
    db: Session = Depends(get_db),
):
    disposition = get_disposition_or_404(
        disposition_id,
        db,
    )

    if disposition.disposition_status in {
        DispositionStatus.completed.value,
        DispositionStatus.cancelled.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Disposition {disposition_id} is "
                f"{disposition.disposition_status} and cannot be modified"
            ),
        )

    update_data = payload.model_dump(
        exclude_unset=True,
    )

    if "disposition_type" in update_data:
        update_data["disposition_type"] = (
            update_data["disposition_type"].value
        )

    if "currency" in update_data and update_data["currency"] is not None:
        update_data["currency"] = update_data["currency"].upper()

    for field, value in update_data.items():
        setattr(
            disposition,
            field,
            value,
        )

    db.commit()
    db.refresh(disposition)

    return disposition


@router.patch(
    "/{disposition_id}/status",
    response_model=AssetDispositionResponse,
)
def update_asset_disposition_status(
    disposition_id: int,
    payload: AssetDispositionStatusUpdate,
    db: Session = Depends(get_db),
):
    disposition = get_disposition_or_404(
        disposition_id,
        db,
    )

    current_status = DispositionStatus(
        disposition.disposition_status
    )

    requested_status = payload.disposition_status

    allowed_transitions = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    if requested_status not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid disposition status transition: "
                f"{current_status.value} -> "
                f"{requested_status.value}"
            ),
        )

    if requested_status == DispositionStatus.completed:
        asset = get_asset_or_404(
            disposition.asset_id,
            db,
        )

        existing_completed = db.scalar(
            select(AssetDisposition)
            .where(
                AssetDisposition.asset_id == disposition.asset_id,
                AssetDisposition.id != disposition.id,
                AssetDisposition.disposition_status
                == DispositionStatus.completed.value,
            )
            .limit(1)
        )

        if existing_completed is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Asset {disposition.asset_id} already has "
                    "another completed disposition"
                ),
            )

        if (
            DispositionType(disposition.disposition_type)
            in REUSE_DISPOSITIONS
        ):
            if asset.data_wipe_status != "passed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Data sanitization must be passed before "
                        "completing a resale, reuse, internal-use, "
                        "or donation disposition"
                    ),
                )

    disposition.disposition_status = requested_status.value

    if requested_status == DispositionStatus.completed:
        asset = get_asset_or_404(
            disposition.asset_id,
            db,
        )

        asset.status = "disposed"

    db.commit()
    db.refresh(disposition)

    return disposition