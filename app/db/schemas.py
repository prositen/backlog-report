from typing import Optional

from pydantic import BaseModel, field_validator

from app.db.models import Label


class StoryBase(BaseModel):
    id: int
    name: str
    shortcut_url: str
    description: str
    created: str
    updated: str
    labels: list[str]
    persons: list['Person']
    components: list['Component']
    epic_groups: list['EpicGroup']
    products: list['Product']

    active: bool
    priority: Optional[str]
    period: Optional[str]

    @field_validator('labels', mode='before')
    @classmethod
    def transform_labels(cls, raw_labels: list['Label']) -> list[str]:
        return [rl.name for rl in raw_labels]

    class Config:
        from_attributes = True
        populate_by_name = True


class StoryWithPrio(StoryBase):
    pass


class CustomFieldWithValue(BaseModel):
    name: str
    value: str

    class Config:
        from_attributes = True
        populate_by_name = True


class CustomFieldBase(BaseModel):
    id: str
    name: str


class Objective(BaseModel):
    id: str
    name: str


class LabelBase(BaseModel):
    id: int
    name: str


class LabelNames(BaseModel):
    name: str


class BacklogResponse(BaseModel):
    items: list[StoryBase]
    count: int
    total: int


class ReportFieldBase(BaseModel):
    name: str


class ReportField(ReportFieldBase):
    id: int


class Person(ReportField):
    pass


class Component(ReportField):
    pass


class EpicGroup(ReportField):
    pass


class Product(ReportField):
    pass
