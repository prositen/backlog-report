from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, Select, asc, desc
from sqlalchemy.orm import Session

from app.db.models import Story, Label, StoryCustomFields, Person
from app.db.schemas import BacklogResponse
from app.routers.admin.shortcut import get_db

router = APIRouter(prefix='/shortcut', tags=['shortcut', 'stories'])


class SortOrder(Enum):
    reverse = 'reverse'
    forward = 'forward'


async def search_params(
        q: Optional[str] = Query(
            None,
            description='Search in story name and description',
            examples='tidsbokning'
        ),
        sort_name: Optional[SortOrder] = Query(
            None,
            description='Sort stories on name',
            alias='sort[name]'
        ),
        sort_id: Optional[SortOrder] = Query(
            None,
            description='Sort stories on ID',
            alias='sort[id]'
        ),
        sort_created: Optional[SortOrder] = Query(
            None,
            description='Sort stories on created date',
            alias='sort[created]'
        ),
        sort_updated: Optional[SortOrder] = Query(
            None,
            description='Sort stories on update date',
            alias='sort[updated]'
        ),
        sort_priority: Optional[SortOrder] = Query(
            None,
            description='Sort stories on priority',
            alias='sort[priority]'
        ),
        filter_priority: Optional[str] = Query(
            None,
            description='Filter stories on priority',
            alias='filter[priority]'
        ),
        sort_period: Optional[SortOrder] = Query(
            None,
            description='Sort stories on period',
            alias='sort[period]'
        ),
        filter_period: Optional[str] = Query(
            None,
            description='Filter stories on period',
            alias='filter[period]'
        ),
        filter_label: Optional[str] = Query(
            None,
            description='Filter stories on label',
            alias='filter[label]'
        )
):
    return {'q': q,
            'sort[name]': sort_name,
            'sort[id]': sort_id,
            'sort[created]': sort_created,
            'sort[updated]': sort_updated,
            'sort[priority]': sort_priority, 'filter[priority]': filter_priority,
            'sort[period]': sort_period, 'filter[period]': filter_period,
            'filter[label]': filter_label}


async def apply_story_filters(query: Select, params: dict):
    if value := params.get('q'):
        query = query.filter(
            Story.name.ilike(f'%{value}%') | Story.description.ilike(f'%{value}%'))
    if value := params.get('filter[priority]'):
        if value.lower() in ('', 'null', 'None', 'saknas'):
            query = query.filter(
                ~Story.custom_fields.any(StoryCustomFields.name == 'Priority'))
        else:
            query = query.filter(StoryCustomFields.name == 'Priority',
                                 StoryCustomFields.value.ilike(value))
    if value := params.get('filter[period]'):
        if value.lower() in ('', 'null', 'None', 'saknas'):
            query = query.filter(
                ~Story.custom_fields.any(StoryCustomFields.name == 'Periodsplanering'))
        else:
            query = query.filter(StoryCustomFields.name == 'Periodsplanering',
                                 StoryCustomFields.value.ilike(value))
    if value := params.get('filter[label]'):
        query = query.filter(Label.name == value)
    return query


async def apply_story_sort(query: Select, params: dict):
    order = {
        SortOrder.forward: asc,
        SortOrder.reverse: desc
    }
    if value := params.get('sort[name]'):
        query = query.order_by(order[value](Story.name))
    if value := params.get('sort[id]'):
        query = query.order_by(order[value](Story.id))
    if value := params.get('sort[created]'):
        query = query.order_by(order[value](Story.created))
    if value := params.get('sort[updated]'):
        query = query.order_by(order[value](Story.updated))
    return query


def prio_sort(prio):
    match prio:
        case 'High':
            return 4
        case 'Medium':
            return 3
        case 'Low':
            return 2
        case None | 'None' | _:
            return 1


def period_sort(period):
    match period:
        case 'P1 2024':
            return 1
        case 'P2 2024':
            return 2
        case 'P3 2024':
            return 3
        case 'Kanske nästa period':
            return 4
        case 'Kanske efter nästa period':
            return 5
        case None | 'None' | _:
            return 6


@router.get('/backlog')
async def get_backlog(params: dict = Depends(search_params),
                      db: Session = Depends(get_db)) -> BacklogResponse:
    query = select(Story) \
        .join(Label, Story.labels, isouter=True) \
        .join(StoryCustomFields, Story.custom_fields, isouter=True) \
        .join(Person, Story.persons, isouter=True)

    total = db.execute(select(func.count(Story.id))).scalar()

    query = await apply_story_filters(query, params)
    query = await apply_story_sort(query, params)

    matching = db.execute(query).unique().scalars().all()

    if value := params.get('sort[priority]'):
        matching = sorted(matching, key=lambda c: prio_sort(c.priority),
                          reverse=(value == SortOrder.reverse))
    if value := params.get('sort[period]'):
        matching = sorted(matching, key=lambda c: period_sort(c.period),
                          reverse=(value == SortOrder.reverse))
    return {
        'items': matching,
        'count': len(matching),
        'total': total
    }
