from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.asset_category import AssetCategory
from app.models.qc_template import QCTemplate
from app.models.qc_template_item import QCTemplateItem
from app.schemas.qc_template import (
    QCTemplateCreate,
    QCTemplateResponse,
)


router = APIRouter(
    prefix="/api/qc-templates",
    tags=["QC Templates"],
)


def _get_template_query():
    return (
        select(QCTemplate)
        .options(
            joinedload(QCTemplate.items),
            joinedload(QCTemplate.category),
        )
    )


@router.post(
    "",
    response_model=QCTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_qc_template(
    template_data: QCTemplateCreate,
    db: Session = Depends(get_db),
):
    category = db.get(AssetCategory, template_data.category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset category not found.",
        )

    existing_template = db.scalar(
        select(QCTemplate).where(
            QCTemplate.category_id == template_data.category_id,
            QCTemplate.code == template_data.code,
            QCTemplate.version == template_data.version,
        )
    )

    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A QC template with this category, code, and version "
                "already exists."
            ),
        )

    template = QCTemplate(
        category_id=template_data.category_id,
        code=template_data.code,
        name=template_data.name,
        description=template_data.description,
        version=template_data.version,
        is_active=False,
    )

    for item_data in template_data.items:
        item = QCTemplateItem(
            item_code=item_data.item_code,
            label=item_data.label,
            description=item_data.description,
            response_type=item_data.response_type.value,
            is_required=item_data.is_required,
            sort_order=item_data.sort_order,
            options=item_data.options,
        )
        template.items.append(item)

    db.add(template)

    try:
        db.flush()

        if template_data.is_active:
            db.execute(
                select(AssetCategory)
                .where(
                    AssetCategory.id == template_data.category_id,
                )
                .with_for_update()
            )

            db.query(QCTemplate).filter(
                QCTemplate.category_id == template_data.category_id,
                QCTemplate.id != template.id,
                QCTemplate.is_active.is_(True),
            ).update(
                {
                    QCTemplate.is_active: False,
                },
                synchronize_session=False,
            )

            template.is_active = True

        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create the QC template because it conflicts "
                "with an existing template."
            ),
        )

    db.refresh(template)

    result = db.scalar(
        _get_template_query().where(
            QCTemplate.id == template.id,
        )
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QC template was created but could not be loaded.",
        )

    return result


@router.get(
    "",
    response_model=list[QCTemplateResponse],
)
def list_qc_templates(
    category_id: int | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = _get_template_query()

    if category_id is not None:
        query = query.where(
            QCTemplate.category_id == category_id,
        )

    if not include_inactive:
        query = query.where(
            QCTemplate.is_active.is_(True),
        )

    query = query.order_by(
        QCTemplate.category_id,
        QCTemplate.code,
        QCTemplate.version,
        QCTemplate.id,
    )

    return db.scalars(
        query
    ).unique().all()


@router.get(
    "/{template_id}",
    response_model=QCTemplateResponse,
)
def get_qc_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    template = db.scalar(
        _get_template_query().where(
            QCTemplate.id == template_id,
        )
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QC template not found.",
        )

    return template


@router.post(
    "/{template_id}/activate",
    response_model=QCTemplateResponse,
)
def activate_qc_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    template = db.get(QCTemplate, template_id)

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QC template not found.",
        )

    db.execute(
        select(AssetCategory)
        .where(
            AssetCategory.id == template.category_id,
        )
        .with_for_update()
    )

    if template.is_active:
        result = db.scalar(
            _get_template_query().where(
                QCTemplate.id == template_id,
            )
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Active QC template could not be loaded.",
            )

        return result

    db.query(QCTemplate).filter(
        QCTemplate.category_id == template.category_id,
        QCTemplate.id != template.id,
        QCTemplate.is_active.is_(True),
    ).update(
        {
            QCTemplate.is_active: False,
        },
        synchronize_session=False,
    )

    template.is_active = True

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to activate the QC template because another "
                "active template exists for this category."
            ),
        )

    result = db.scalar(
        _get_template_query().where(
            QCTemplate.id == template_id,
        )
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="QC template was activated but could not be loaded.",
        )

    return result