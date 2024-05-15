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


class LabelBase(BaseModel):
    id: int
    name: str


class PersonBase(BaseModel):
    name: str


class PersonCreate(PersonBase):
    pass


class Person(PersonBase):
    id: int


class LabelNames(BaseModel):
    name: str


class BacklogResponse(BaseModel):
    items: list[StoryBase]
    count: int
    total: int
