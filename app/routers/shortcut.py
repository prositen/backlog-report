from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Story
from app.db.schemas import StoryBase
from app.routers.admin.shortcut import get_db

router = APIRouter(prefix='/shortcut', tags=['shortcut', 'admin'])


class StoryFilter(Filter):
    class Constants(Filter.Constants):
        model = Story
    order_by: Optional[list[str]] = None


@router.get('/backlog')
async def get_backlog(story_filter: Optional[StoryFilter] = FilterDepends(StoryFilter),
                      db: Session = Depends(get_db)) -> Page[StoryBase]:
    query = select(Story) \
        .options(joinedload(Story.labels)) \
        .options(joinedload(Story.custom_fields))


    query = story_filter.sort(query)

    return paginate(db, query)

    # TODO: Filter on Periodsplanering
    #       Filter on Priority
    #       Filter on BO/PO: Att prioritera
