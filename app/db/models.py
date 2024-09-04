from typing import List

from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

story_labels = Table('story_labels',
                     Base.metadata,
                     Column('story_id', ForeignKey('stories.id')),
                     Column('label_id', ForeignKey('labels.id')))

story_persons = Table('story_persons',
                      Base.metadata,
                      Column('story_id', ForeignKey('stories.id')),
                      Column('person_id', ForeignKey('persons.id')))

story_components = Table('story_components',
                         Base.metadata,
                         Column('story_id', ForeignKey('stories.id')),
                         Column('component_id', ForeignKey('components.id')))

story_epic_groups = Table('story_epic_groups',
                          Base.metadata,
                          Column('story_id', ForeignKey('stories.id')),
                          Column('epic_group_id', ForeignKey('epic_groups.id')))

story_products = Table('story_products',
                       Base.metadata,
                       Column('story_id', ForeignKey('stories.id')),
                       Column('product_id', ForeignKey('products.id')))


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
    story: Mapped['Story'] = relationship(back_populates='custom_fields')


class Story(Base):
    __tablename__ = 'stories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created: Mapped[str]
    updated: Mapped[str]
    shortcut_url: Mapped[str]
    description: Mapped[str]
    active: Mapped[bool]

    # From shortcut
    custom_fields: Mapped[List['StoryCustomFields']] = relationship(
        back_populates='story', cascade='all, delete-orphan')
    labels: Mapped[List['Label']] = relationship(secondary=story_labels)

    # Locally administrated
    persons: Mapped[List['Person']] = relationship(secondary=story_persons)
    components: Mapped[List['Component']] = relationship(secondary=story_components)
    epic_groups: Mapped[List['EpicGroup']] = relationship(secondary=story_epic_groups)
    products: Mapped[List['Product']] = relationship(secondary=story_products)

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


class CustomField(Base):
    __tablename__ = 'custom_fields'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    field_values: Mapped[List['CustomFieldValue']] = relationship(back_populates='field',
                                                                  cascade='all, delete-orphan')


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


class ReportBase:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Person(Base, ReportBase):
    __tablename__ = 'persons'


class Component(Base, ReportBase):
    __tablename__ = 'components'


class EpicGroup(Base, ReportBase):
    __tablename__ = 'epic_groups'


class Product(Base, ReportBase):
    __tablename__ = 'products'
