from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_disposition import AssetDisposition
from app.models.asset_sanitization import AssetSanitization
from app.schemas.asset_disposition import AssetDispositionResponse
from app.schemas.asset_return import AssetReturnCreate


router = APIRouter(
    prefix="/api/assets",
    tags=["Asset Returns"],
)


@router.post(
    "/{asset_id}/return",
    response_model=AssetDispositionResponse,
    status_code=status.HTTP_201_CREATED,
)
def return_asset(
    asset_id: int,
    data: AssetReturnCreate,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Lock the Asset row for the duration of this transaction.
    #
    # This prevents two simultaneous return requests from both
    # successfully reactivating the same disposed asset.
    # ---------------------------------------------------------

    asset = db.scalar(
        select(Asset)
        .where(Asset.id == asset_id)
        .with_for_update()
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    # ---------------------------------------------------------
    # A return is only valid for an asset that is currently
    # disposed.
    # ---------------------------------------------------------

    if asset.status != "disposed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot return asset with status "
                f"'{asset.status}'. Asset must be disposed."
            ),
        )

    # ---------------------------------------------------------
    # Verify that the asset has a completed previous
    # disposition.
    #
    # The previous disposition remains historical and is NOT
    # modified.
    # ---------------------------------------------------------

    completed_disposition = db.scalar(
        select(AssetDisposition)
        .where(
            AssetDisposition.asset_id == asset.id,
            AssetDisposition.disposition_status == "completed",
        )
        .order_by(
            AssetDisposition.id.desc()
        )
        .limit(1)
    )

    if completed_disposition is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Asset cannot be returned because it has no "
                "completed disposition."
            ),
        )

    # ---------------------------------------------------------
    # Preserve the current sanitization state as historical
    # data if it has not already been recorded.
    #
    # This is important for assets that were sanitized before
    # asset_sanitizations history was introduced.
    # ---------------------------------------------------------

    latest_sanitization = db.scalar(
        select(AssetSanitization)
        .where(
            AssetSanitization.asset_id == asset.id
        )
        .order_by(
            AssetSanitization.id.desc()
        )
        .limit(1)
    )

    current_wipe_has_history = (
        latest_sanitization is not None
        and latest_sanitization.data_wipe_status
        == asset.data_wipe_status
        and latest_sanitization.data_wipe_method
        == asset.data_wipe_method
        and latest_sanitization.data_wipe_date
        == asset.data_wipe_date
        and latest_sanitization.data_wipe_reference
        == asset.data_wipe_reference
    )

    if not current_wipe_has_history:
        db.add(
            AssetSanitization(
                asset_id=asset.id,
                data_wipe_status=asset.data_wipe_status,
                data_wipe_method=asset.data_wipe_method,
                data_wipe_date=asset.data_wipe_date,
                data_wipe_reference=asset.data_wipe_reference,
            )
        )

    # ---------------------------------------------------------
    # Create a NEW sanitization cycle for the reactivated
    # asset.
    #
    # The new cycle starts as not_started. Subsequent
    # data-sanitization operations will update this record.
    # ---------------------------------------------------------

    db.add(
        AssetSanitization(
            asset_id=asset.id,
            data_wipe_status="not_started",
            data_wipe_method=None,
            data_wipe_date=None,
            data_wipe_reference=None,
        )
    )

    # ---------------------------------------------------------
    # Create the historical returned disposition.
    #
    # The previous completed disposition is never modified.
    # ---------------------------------------------------------

    returned_disposition = AssetDisposition(
        asset_id=asset.id,
        disposition_type="returned",
        disposition_status="completed",
        disposition_date=(
            data.disposition_date
            if data.disposition_date is not None
            else datetime.now(timezone.utc)
        ),
        processed_by=data.processed_by,
        disposition_reference=data.disposition_reference,
        recipient_name=data.recipient_name,
        recipient_reference=data.recipient_reference,
        notes=data.notes,
    )

    db.add(returned_disposition)

    # ---------------------------------------------------------
    # Reactivate the EXISTING Asset record.
    #
    # Asset ID, asset code, serial number, collection
    # relationships, inspections, processing records and
    # disposition history remain unchanged.
    # ---------------------------------------------------------

    asset.status = "received"
    asset.final_disposition = None

    # ---------------------------------------------------------
    # Reset only the CURRENT sanitization state.
    #
    # The previous sanitization state has already been preserved
    # above, and the new sanitization cycle has been created.
    # ---------------------------------------------------------

    asset.data_wipe_status = "not_started"
    asset.data_wipe_method = None
    asset.data_wipe_date = None
    asset.data_wipe_reference = None

    # ---------------------------------------------------------
    # Commit the complete return transaction.
    #
    # The returned disposition, sanitization history and Asset
    # reactivation are committed together.
    # ---------------------------------------------------------

    db.commit()

    db.refresh(returned_disposition)

    return returned_disposition