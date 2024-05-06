from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

story_labels = Table('story_labels',
                     Base.metadata,
                     Column('story_id', ForeignKey('stories.id')),
                     Column('label_id', ForeignKey('labels.id')))


class StoryCustomFields(Base):
    __tablename__ = 'story_custom_fields'
    story_id: Mapped[int] = mapped_column(ForeignKey('stories.id'), primary_key=True)
    custom_field_value_id: Mapped[str] = mapped_column(ForeignKey('custom_field_values.value_id'),
                                                       primary_key=True)
    custom_field_value: Mapped['CustomFieldValue'] = relationship()
    value: AssociationProxy[str] = association_proxy(target_collection='custom_field_value',
                                                     attr='value')
    name: AssociationProxy[str] = association_proxy(target_collection='custom_field_value',
                                                    attr='name')


class Story(Base):
    __tablename__ = 'stories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created: Mapped[str]
    updated: Mapped[str]
    shortcut_url: Mapped[str]
    description: Mapped[str]
    custom_fields: Mapped[List['StoryCustomFields']] = relationship(
        backref='story_custom_fields')
    labels: Mapped[List['Label']] = relationship(secondary=story_labels)

    @hybrid_property
    def priority(self):
        for cf in self.custom_fields:
            if cf.name == 'Priority':
                return cf.value
        return None

    @hybrid_property
    def period(self):
        for cf in self.custom_fields:
            if cf.name == 'Periodsplanering':
                return cf.value
        return None

    @hybrid_property
    def label_names(self):
        return [label.name for label in self.labels]


class CustomField(Base):
    __tablename__ = 'custom_fields'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    field_values: Mapped[List['CustomFieldValue']] = relationship(back_populates='field')


class CustomFieldValue(Base):
    __tablename__ = 'custom_field_values'
    field_id: Mapped[str] = mapped_column(ForeignKey('custom_fields.id'))
    value_id: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]
    field: Mapped['CustomField'] = relationship(back_populates='field_values')
    name: AssociationProxy[str] = association_proxy(target_collection='field', attr='name')


class Label(Base):
    __tablename__ = 'labels'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
