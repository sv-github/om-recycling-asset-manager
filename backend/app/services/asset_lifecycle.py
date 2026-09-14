from __future__ import annotations

from enum import StrEnum

from fastapi import HTTPException, status


class AssetLifecycleStatus(StrEnum):
    RECEIVED = "received"
    IN_PROCESS = "in_process"
    READY = "ready"
    DISPOSED = "disposed"
    ON_HOLD = "on_hold"
    CLOSED = "closed"


ACTIVE_STATUSES = {
    AssetLifecycleStatus.RECEIVED,
    AssetLifecycleStatus.IN_PROCESS,
    AssetLifecycleStatus.READY,
}

VALID_TRANSITIONS: dict[AssetLifecycleStatus, set[AssetLifecycleStatus]] = {
    AssetLifecycleStatus.RECEIVED: {
        AssetLifecycleStatus.IN_PROCESS,
        AssetLifecycleStatus.ON_HOLD,
    },
    AssetLifecycleStatus.IN_PROCESS: {
        AssetLifecycleStatus.READY,
        AssetLifecycleStatus.ON_HOLD,
    },
    AssetLifecycleStatus.READY: {
        AssetLifecycleStatus.IN_PROCESS,
        AssetLifecycleStatus.DISPOSED,
        AssetLifecycleStatus.ON_HOLD,
    },
    AssetLifecycleStatus.ON_HOLD: {
        AssetLifecycleStatus.RECEIVED,
        AssetLifecycleStatus.IN_PROCESS,
        AssetLifecycleStatus.READY,
    },
    AssetLifecycleStatus.DISPOSED: {
        AssetLifecycleStatus.RECEIVED,
        AssetLifecycleStatus.CLOSED,
    },
    AssetLifecycleStatus.CLOSED: set(),
}


def normalize_status(value: str) -> AssetLifecycleStatus:
    try:
        return AssetLifecycleStatus(value.strip().lower())
    except (AttributeError, ValueError) as exc:
        allowed = ", ".join(item.value for item in AssetLifecycleStatus)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid asset lifecycle status. Allowed values: {allowed}.",
        ) from exc


def transition_asset(
    asset,
    target_status: AssetLifecycleStatus | str,
    *,
    reason: str | None = None,
) -> None:
    """Apply one legal Asset.status transition."""
    current = normalize_status(asset.status)
    target = normalize_status(
        target_status.value
        if isinstance(target_status, AssetLifecycleStatus)
        else target_status
    )

    if current == target:
        return

    if target not in VALID_TRANSITIONS[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid asset lifecycle transition: "
                f"{current.value} -> {target.value}."
            ),
        )

    if target == AssetLifecycleStatus.ON_HOLD:
        if not reason or not reason.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A reason is required when placing an asset on hold.",
            )
        asset.lifecycle_previous_status = current.value
        asset.lifecycle_hold_reason = reason.strip()

    elif current == AssetLifecycleStatus.ON_HOLD:
        expected = asset.lifecycle_previous_status
        if expected is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Asset is on hold but has no previous lifecycle status.",
            )
        if target.value != expected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "An on-hold asset can only return to its previous "
                    f"lifecycle status '{expected}'."
                ),
            )
        asset.lifecycle_previous_status = None
        asset.lifecycle_hold_reason = None

    asset.status = target.value


def ensure_active_asset(asset) -> None:
    current = normalize_status(asset.status)
    if current not in ACTIVE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Asset cannot be modified while its lifecycle status is "
                f"'{current.value}'."
            ),
        )
