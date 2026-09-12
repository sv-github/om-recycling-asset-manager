from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_disposition import AssetDisposition
from app.models.asset_inspection import AssetInspection
from app.models.asset_processing import AssetProcessing
from app.models.asset_sanitization import AssetSanitization
from app.schemas.asset_history import (
    AssetHistoryEvent,
    AssetHistoryResponse,
)


router = APIRouter(
    prefix="/api/assets",
    tags=["Asset History"],
)


def _enum_value(value: Any) -> Any:
    """
    Return the underlying value for Enum instances.
    """
    if isinstance(value, Enum):
        return value.value

    return value


def _event_date(
    record: Any,
    preferred_fields: tuple[str, ...],
) -> datetime:
    """
    Resolve the operational date for a history event.

    The event-specific operational date is preferred.
    created_at is used as the fallback.
    """

    for field_name in preferred_fields:
        value = getattr(record, field_name, None)

        if value is not None:
            if isinstance(value, datetime):
                return value

            if isinstance(value, date):
                return datetime.combine(
                    value,
                    time.min,
                    tzinfo=timezone.utc,
                )

    created_at = getattr(record, "created_at", None)

    if isinstance(created_at, datetime):
        return created_at

    if isinstance(created_at, date):
        return datetime.combine(
            created_at,
            time.min,
            tzinfo=timezone.utc,
        )

    raise ValueError(
        f"Unable to determine history event date for "
        f"{type(record).__name__}."
    )


def _event_status(
    record: Any,
    preferred_fields: tuple[str, ...],
) -> str | None:
    """
    Resolve the status field without coupling the history API
    to unnecessary model-specific schema details.
    """

    for field_name in preferred_fields:
        value = getattr(record, field_name, None)

        if value is not None:
            return str(_enum_value(value))

    return None


def _details(record: Any) -> dict[str, Any]:
    """
    Return the model's database columns as event details.

    Identity and audit timestamp fields are already represented
    elsewhere in the history event and are therefore omitted.
    """

    excluded_fields = {
        "id",
        "asset_id",
        "created_at",
        "updated_at",
    }

    mapper = sqlalchemy_inspect(record).mapper

    details: dict[str, Any] = {}

    for column in mapper.column_attrs:
        field_name = column.key

        if field_name in excluded_fields:
            continue

        value = getattr(record, field_name)

        details[field_name] = _enum_value(value)

    return details


def _build_event(
    *,
    record: Any,
    event_type: str,
    title: str,
    date_fields: tuple[str, ...],
    status_fields: tuple[str, ...],
) -> AssetHistoryEvent:
    return AssetHistoryEvent(
        event_type=event_type,
        event_id=record.id,
        event_date=_event_date(
            record,
            date_fields,
        ),
        title=title,
        status=_event_status(
            record,
            status_fields,
        ),
        details=_details(record),
    )


@router.get(
    "/{asset_id}/history",
    response_model=AssetHistoryResponse,
)
def get_asset_history(
    asset_id: int,
    db: Session = Depends(get_db),
):
    """
    Return the complete read-only lifecycle history for an asset.

    History is aggregated from the existing:
    - inspection records
    - processing records
    - sanitization records
    - disposition records

    A completed disposition whose type is "returned" is represented
    as a "return" history event.

    No lifecycle state is modified by this endpoint.
    """

    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    inspection_records = db.scalars(
        select(AssetInspection)
        .where(
            AssetInspection.asset_id == asset_id
        )
        .order_by(
            AssetInspection.id.asc()
        )
    ).all()

    processing_records = db.scalars(
        select(AssetProcessing)
        .where(
            AssetProcessing.asset_id == asset_id
        )
        .order_by(
            AssetProcessing.id.asc()
        )
    ).all()

    sanitization_records = db.scalars(
        select(AssetSanitization)
        .where(
            AssetSanitization.asset_id == asset_id
        )
        .order_by(
            AssetSanitization.id.asc()
        )
    ).all()

    disposition_records = db.scalars(
        select(AssetDisposition)
        .where(
            AssetDisposition.asset_id == asset_id
        )
        .order_by(
            AssetDisposition.id.asc()
        )
    ).all()

    events: list[AssetHistoryEvent] = []

    for record in inspection_records:
        events.append(
            _build_event(
                record=record,
                event_type="inspection",
                title="Inspection",
                date_fields=("inspection_date",),
                status_fields=(
                    "inspection_status",
                    "status",
                ),
            )
        )

    for record in processing_records:
        events.append(
            _build_event(
                record=record,
                event_type="processing",
                title="Processing",
                date_fields=("processing_date",),
                status_fields=(
                    "processing_status",
                    "status",
                ),
            )
        )

    for record in sanitization_records:
        events.append(
            _build_event(
                record=record,
                event_type="sanitization",
                title="Data Sanitization",
                date_fields=("data_wipe_date",),
                status_fields=("data_wipe_status",),
            )
        )

    for record in disposition_records:
        disposition_type = _enum_value(
            getattr(record, "disposition_type", None)
        )

        if disposition_type == "returned":
            event_type = "return"
            title = "Asset Returned"
        else:
            event_type = "disposition"
            title = "Disposition"

        events.append(
            _build_event(
                record=record,
                event_type=event_type,
                title=title,
                date_fields=("disposition_date",),
                status_fields=("disposition_status",),
            )
        )

    # Oldest event first.
    #
    # event_id is the secondary ordering key as defined by the
    # 4B-7 contract. event_type provides a deterministic tertiary
    # ordering when independent tables happen to use the same ID.
    events.sort(
        key=lambda event: (
            event.event_date,
            event.event_id,
            event.event_type,
        )
    )

    return AssetHistoryResponse(
        asset_id=asset.id,
        asset_code=asset.asset_code,
        events=events,
    )