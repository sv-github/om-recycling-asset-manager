from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.qc_template_item import (
    QCTemplateItemCreate,
    QCTemplateItemResponse,
)


class QCTemplateBase(BaseModel):
    category_id: int = Field(gt=0)
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    version: int = Field(ge=1)
    is_active: bool = False

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("code must not be empty or whitespace")

        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("name must not be empty or whitespace")

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class QCTemplateCreate(QCTemplateBase):
    items: list[QCTemplateItemCreate] = Field(min_length=1)


class QCTemplateResponse(QCTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    items: list[QCTemplateItemResponse] = Field(default_factory=list)