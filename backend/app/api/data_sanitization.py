from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_sanitization import AssetSanitization
from app.schemas.data_sanitization import (
    DataSanitizationResponse,
    DataSanitizationUpdate,
)


router = APIRouter(
    prefix="/api/assets",
    tags=["Asset Processing / Data Sanitization"],
)


ALLOWED_STATUSES = {
    "not_started",
    "in_progress",
    "passed",
    "failed",
}


VALID_TRANSITIONS = {
    "not_started": {"in_progress"},
    "in_progress": {"passed", "failed"},
    "failed": {"in_progress"},
    "passed": set(),
}


@router.patch(
    "/{asset_id}/data-sanitization",
    response_model=DataSanitizationResponse,
    status_code=status.HTTP_200_OK,
)
def update_data_sanitization(
    asset_id: int,
    data: DataSanitizationUpdate,
    db: Session = Depends(get_db),
):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status in {"closed", "disposed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot modify data sanitization for an asset "
                f"with status '{asset.status}'."
            ),
        )

    new_status = data.data_wipe_status.strip().lower()

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid data wipe status. Allowed values: "
                "not_started, in_progress, passed, failed."
            ),
        )

    current_status = (
        asset.data_wipe_status.strip().lower()
        if asset.data_wipe_status
        else "not_started"
    )

    if current_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Asset has an unsupported existing data wipe status: "
                f"{asset.data_wipe_status}"
            ),
        )

    # Allow the same status to be submitted again.
    # Different statuses must follow the defined workflow.
    if new_status != current_status:
        allowed_next_states = VALID_TRANSITIONS[current_status]

        if new_status not in allowed_next_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid data wipe status transition: "
                    f"{current_status} -> {new_status}"
                ),
            )

    # A successful sanitization must have complete audit information.
    if new_status == "passed":

        if not data.data_wipe_method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "data_wipe_method is required when "
                    "data_wipe_status is 'passed'."
                ),
            )

        if not data.data_wipe_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "data_wipe_date is required when "
                    "data_wipe_status is 'passed'."
                ),
            )

        if not data.data_wipe_reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "data_wipe_reference is required when "
                    "data_wipe_status is 'passed'."
                ),
            )

    # ---------------------------------------------------------
    # Find or create the current sanitization cycle
    # ---------------------------------------------------------

    sanitization = db.scalar(
        select(AssetSanitization)
        .where(AssetSanitization.asset_id == asset.id)
        .order_by(
            AssetSanitization.id.desc()
        )
        .limit(1)
    )

    if sanitization is None:
        sanitization = AssetSanitization(
            asset_id=asset.id,
            data_wipe_status=new_status,
            data_wipe_method=data.data_wipe_method,
            data_wipe_date=data.data_wipe_date,
            data_wipe_reference=data.data_wipe_reference,
        )

        db.add(sanitization)

    else:
        sanitization.data_wipe_status = new_status

        if data.data_wipe_method is not None:
            sanitization.data_wipe_method = data.data_wipe_method

        if data.data_wipe_date is not None:
            sanitization.data_wipe_date = data.data_wipe_date

        if data.data_wipe_reference is not None:
            sanitization.data_wipe_reference = data.data_wipe_reference

    # ---------------------------------------------------------
    # Update the Asset's current sanitization state
    # ---------------------------------------------------------

    asset.data_wipe_status = new_status

    if data.data_wipe_method is not None:
        asset.data_wipe_method = data.data_wipe_method

    if data.data_wipe_date is not None:
        asset.data_wipe_date = data.data_wipe_date

    if data.data_wipe_reference is not None:
        asset.data_wipe_reference = data.data_wipe_reference

    # Automatically timestamp a successful sanitization if
    # no date was supplied.
    if new_status == "passed" and asset.data_wipe_date is None:
        asset.data_wipe_date = datetime.now(timezone.utc)

        sanitization.data_wipe_date = asset.data_wipe_date

    # Keep the history record synchronized with the final
    # current Asset values.
    sanitization.data_wipe_method = asset.data_wipe_method
    sanitization.data_wipe_date = asset.data_wipe_date
    sanitization.data_wipe_reference = asset.data_wipe_reference

    # ---------------------------------------------------------
    # Commit Asset + sanitization history together
    # ---------------------------------------------------------

    db.commit()
    db.refresh(asset)

    # ---------------------------------------------------------
    # Return the dedicated sanitization response schema.
    # Do NOT return the Asset object directly because the
    # response schema uses asset_id rather than id.
    # ---------------------------------------------------------

    return DataSanitizationResponse(
        asset_id=asset.id,
        asset_code=asset.asset_code,
        data_wipe_status=asset.data_wipe_status,
        data_wipe_method=asset.data_wipe_method,
        data_wipe_date=asset.data_wipe_date,
        data_wipe_reference=asset.data_wipe_reference,
    )