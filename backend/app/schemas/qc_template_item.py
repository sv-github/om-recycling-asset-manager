from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QCResponseType(str, Enum):
    PASS_FAIL = "PASS_FAIL"
    CONDITION = "CONDITION"
    COMPONENT = "COMPONENT"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"


PASS_FAIL_OPTIONS = [
    "pass",
    "fail",
    "not_tested",
    "not_applicable",
]

CONDITION_OPTIONS = [
    "good",
    "fair",
    "poor",
    "damaged",
    "not_tested",
    "not_applicable",
]

COMPONENT_OPTIONS = [
    "present",
    "not_present",
    "faulty",
    "not_tested",
    "not_applicable",
]


class QCTemplateItemBase(BaseModel):
    item_code: str = Field(min_length=1, max_length=50)
    label: str = Field(min_length=1, max_length=150)
    description: str | None = None
    response_type: QCResponseType
    is_required: bool = True
    sort_order: int = Field(ge=0)
    options: list[Any] | dict[str, Any] | None = None

    @field_validator("item_code")
    @classmethod
    def normalize_item_code(cls, value: str) -> str:
        value = value.strip().upper()

        if not value:
            raise ValueError("item_code must not be empty or whitespace")

        return value

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("label must not be empty or whitespace")

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_options(self):
        if self.response_type == QCResponseType.PASS_FAIL:
            if self.options is None:
                self.options = PASS_FAIL_OPTIONS.copy()
            elif self.options != PASS_FAIL_OPTIONS:
                raise ValueError(
                    "PASS_FAIL options must be exactly: "
                    "pass, fail, not_tested, not_applicable"
                )

        elif self.response_type == QCResponseType.CONDITION:
            if self.options is None:
                self.options = CONDITION_OPTIONS.copy()
            elif self.options != CONDITION_OPTIONS:
                raise ValueError(
                    "CONDITION options must be exactly: "
                    "good, fair, poor, damaged, not_tested, not_applicable"
                )

        elif self.response_type == QCResponseType.COMPONENT:
            if self.options is None:
                self.options = COMPONENT_OPTIONS.copy()
            elif self.options != COMPONENT_OPTIONS:
                raise ValueError(
                    "COMPONENT options must be exactly: "
                    "present, not_present, faulty, not_tested, not_applicable"
                )

        elif self.response_type in {
            QCResponseType.TEXT,
            QCResponseType.NUMBER,
            QCResponseType.BOOLEAN,
        }:
            if self.options is not None:
                raise ValueError(
                    f"{self.response_type.value} items must not define options"
                )

        return self


class QCTemplateItemCreate(QCTemplateItemBase):
    pass


class QCTemplateItemResponse(QCTemplateItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int