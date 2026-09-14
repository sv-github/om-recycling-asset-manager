from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetCategoryCreate(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    sort_order: int = Field(ge=0)
    is_active: bool = True


class AssetCategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = None
    sort_order: int | None = Field(
        default=None,
        ge=0,
    )
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Category name cannot be null.")
        return value


class AssetCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
