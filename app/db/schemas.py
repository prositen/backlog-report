from typing import Optional

from pydantic import BaseModel, computed_field


class StoryBase(BaseModel):
    id: int
    name: str
    shortcut_url: str
    description: str
    created: str
    updated: str
    # custom_fields: list['CustomFieldWithValue']
    label_names: list[str]
    priority: Optional[str]
    period: Optional[str]

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


class LabelNames(BaseModel):
    name: str
