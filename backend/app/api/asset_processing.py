from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_processing import AssetProcessing
from app.schemas.asset_processing import (
    AssetProcessingCreate,
    AssetProcessingResponse,
    AssetProcessingUpdate,
)


router = APIRouter(
    prefix="/api/asset-processing",
    tags=["Asset Grading / Refurbishment"],
)


ALLOWED_PROCESSING_TYPES = {
    "grading",
    "refurbishment",
    "grading_and_refurbishment",
}

ALLOWED_GRADES = {
    "A",
    "B",
    "C",
    "D",
    "SCRAP",
}

ALLOWED_REFURBISHMENT_STATUSES = {
    "not_required",
    "pending",
    "in_progress",
    "completed",
    "failed",
}


VALID_REFURBISHMENT_TRANSITIONS = {
    "not_required": {
        "pending",
        "in_progress",
    },
    "pending": {
        "in_progress",
    },
    "in_progress": {
        "completed",
        "failed",
    },
    "failed": {
        "pending",
        "in_progress",
    },
    "completed": set(),
}


@router.post(
    "",
    response_model=AssetProcessingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset_processing(
    data: AssetProcessingCreate,
    db: Session = Depends(get_db),
):
    """
    Create a grading/refurbishment processing record for an asset.
    """

    # ---------------------------------------------------------
    # Verify asset exists
    # ---------------------------------------------------------

    asset = db.get(Asset, data.asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot create processing records for an asset "
                f"with status '{asset.status}'."
            ),
        )

    # ---------------------------------------------------------
    # Validate processing type
    # ---------------------------------------------------------

    processing_type = data.processing_type.strip().lower()

    if processing_type not in ALLOWED_PROCESSING_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid processing_type. Allowed values: "
                "grading, refurbishment, "
                "grading_and_refurbishment."
            ),
        )

    # ---------------------------------------------------------
    # Validate grade
    # ---------------------------------------------------------

    grade = None

    if data.grade is not None:
        grade = data.grade.strip().upper()

        if grade not in ALLOWED_GRADES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid grade. Allowed values: "
                    "A, B, C, D, SCRAP."
                ),
            )

    # ---------------------------------------------------------
    # Validate refurbishment status
    # ---------------------------------------------------------

    refurbishment_status = (
        data.refurbishment_status.strip().lower()
    )

    if (
        refurbishment_status
        not in ALLOWED_REFURBISHMENT_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid refurbishment_status. Allowed values: "
                "not_required, pending, in_progress, "
                "completed, failed."
            ),
        )

    # ---------------------------------------------------------
    # Business rules
    # ---------------------------------------------------------

    if (
        processing_type == "grading"
        and refurbishment_status
        not in {"not_required", "completed"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A grading-only record must use "
                "'not_required' or 'completed' "
                "for refurbishment_status."
            ),
        )

    if (
        processing_type in {
            "refurbishment",
            "grading_and_refurbishment",
        }
        and refurbishment_status in {"completed", "failed"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A new refurbishment processing record cannot "
                f"start with status '{refurbishment_status}'. "
                "Use 'pending' or 'in_progress'."
            ),
        )

    if (
        processing_type in {
            "refurbishment",
            "grading_and_refurbishment",
        }
        and refurbishment_status == "completed"
        and grade is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A completed refurbishment must have a grade."
            ),
        )

    # ---------------------------------------------------------
    # Create processing record
    # ---------------------------------------------------------

    processing = AssetProcessing(
        asset_id=data.asset_id,
        processing_type=processing_type,
        grade=grade,
        refurbishment_status=refurbishment_status,
        processor=data.processor,
        processing_date=data.processing_date,
        condition_summary=data.condition_summary,
        repairs_performed=data.repairs_performed,
        parts_replaced=data.parts_replaced,
        testing_notes=data.testing_notes,
        processing_reference=data.processing_reference,
        cost=data.cost,
        notes=data.notes,
    )

    db.add(processing)

    try:
        db.commit()
        db.refresh(processing)
    except Exception:
        db.rollback()
        raise

    return processing


@router.get(
    "/asset/{asset_id}",
    response_model=list[AssetProcessingResponse],
)
def get_asset_processing_history(
    asset_id: int,
    db: Session = Depends(get_db),
):
    """
    Return the complete processing history for an asset.
    """

    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    processing_records = db.scalars(
        select(AssetProcessing)
        .where(AssetProcessing.asset_id == asset_id)
        .order_by(AssetProcessing.processing_date.desc())
    ).all()

    return processing_records


@router.get(
    "/{processing_id}",
    response_model=AssetProcessingResponse,
)
def get_asset_processing(
    processing_id: int,
    db: Session = Depends(get_db),
):
    """
    Return a single processing record.
    """

    processing = db.get(
        AssetProcessing,
        processing_id,
    )

    if processing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset processing record not found.",
        )

    return processing


@router.patch(
    "/{processing_id}",
    response_model=AssetProcessingResponse,
)
def update_asset_processing(
    processing_id: int,
    data: AssetProcessingUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing grading/refurbishment record.
    """

    processing = db.get(
        AssetProcessing,
        processing_id,
    )

    if processing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset processing record not found.",
        )

    asset = db.get(Asset, processing.asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot modify processing records for an asset "
                f"with status '{asset.status}'."
            ),
        )

    # ---------------------------------------------------------
    # Build the complete resulting state first.
    # Do not modify the ORM object until all validation succeeds.
    # ---------------------------------------------------------

    processing_type = processing.processing_type.strip().lower()

    grade = (
        processing.grade.strip().upper()
        if processing.grade is not None
        else None
    )

    refurbishment_status = (
        processing.refurbishment_status.strip().lower()
    )

    # ---------------------------------------------------------
    # Processing type
    # ---------------------------------------------------------

    if data.processing_type is not None:

        processing_type = (
            data.processing_type.strip().lower()
        )

        if processing_type not in ALLOWED_PROCESSING_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid processing_type. Allowed values: "
                    "grading, refurbishment, "
                    "grading_and_refurbishment."
                ),
            )

    # ---------------------------------------------------------
    # Grade
    # ---------------------------------------------------------

    if data.grade is not None:

        grade = data.grade.strip().upper()

        if grade not in ALLOWED_GRADES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid grade. Allowed values: "
                    "A, B, C, D, SCRAP."
                ),
            )

    # ---------------------------------------------------------
    # Refurbishment status
    # ---------------------------------------------------------

    if data.refurbishment_status is not None:

        new_status = (
            data.refurbishment_status.strip().lower()
        )

        if new_status not in ALLOWED_REFURBISHMENT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Invalid refurbishment_status. Allowed values: "
                    "not_required, pending, in_progress, "
                    "completed, failed."
                ),
            )

        current_status = (
            processing.refurbishment_status.strip().lower()
        )

        if new_status != current_status:

            allowed_next_states = (
                VALID_REFURBISHMENT_TRANSITIONS[
                    current_status
                ]
            )

            if new_status not in allowed_next_states:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Invalid refurbishment status "
                        "transition: "
                        f"{current_status} -> {new_status}"
                    ),
                )

        refurbishment_status = new_status

    # ---------------------------------------------------------
    # Validate the COMPLETE resulting combination.
    # These rules mirror the existing CREATE business rules.
    # ---------------------------------------------------------

    if (
        processing_type == "grading"
        and refurbishment_status
        not in {"not_required", "completed"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A grading-only record must use "
                "'not_required' or 'completed' "
                "for refurbishment_status."
            ),
        )

    if (
        processing_type in {
            "refurbishment",
            "grading_and_refurbishment",
        }
        and refurbishment_status == "completed"
        and grade is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A completed refurbishment must have "
                "a grade."
            ),
        )

    # ---------------------------------------------------------
    # Apply changes only after ALL validation succeeds.
    # ---------------------------------------------------------

    processing.processing_type = processing_type
    processing.grade = grade
    processing.refurbishment_status = refurbishment_status

    if data.processor is not None:
        processing.processor = data.processor

    if data.processing_date is not None:
        processing.processing_date = data.processing_date

    if data.condition_summary is not None:
        processing.condition_summary = data.condition_summary

    if data.repairs_performed is not None:
        processing.repairs_performed = data.repairs_performed

    if data.parts_replaced is not None:
        processing.parts_replaced = data.parts_replaced

    if data.testing_notes is not None:
        processing.testing_notes = data.testing_notes

    if data.processing_reference is not None:
        processing.processing_reference = (
            data.processing_reference
        )

    if data.cost is not None:
        processing.cost = data.cost

    if data.notes is not None:
        processing.notes = data.notes

    # ---------------------------------------------------------
    # Commit
    # ---------------------------------------------------------

    try:
        db.commit()
        db.refresh(processing)
    except Exception:
        db.rollback()
        raise

    return processing
