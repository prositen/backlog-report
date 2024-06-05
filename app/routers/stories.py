from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import schemas, models
from app.routers.admin.shortcut import get_db
from app.routers.components import get_component_by_id
from app.routers.epicgroups import get_epic_group_by_id
from app.routers.persons import get_person_by_id
from app.routers.products import get_product_by_id

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/{story_id}", response_model=schemas.StoryBase)
async def get_story_by_id(story_id: int, db: Session = Depends(get_db)):
    query = select(models.Story).where(models.Story.id == story_id) \
        .options(joinedload(models.Story.labels)) \
        .options(joinedload(models.Story.custom_fields)) \
        .options(joinedload(models.Story.persons))
    if story := db.execute(query).unique().scalar_one_or_none():
        return story
    raise HTTPException(404, detail="Story not found")


@router.put('/{story_id}/person/{person_id}', response_model=schemas.StoryBase)
async def add_story_person(story_id: int, person_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    person = await get_person_by_id(person_id, db)
    story.persons.append(person)
    db.commit()
    db.refresh(story)
    return story


@router.delete('/{story_id}/person/{person_id}', response_model=schemas.StoryBase)
async def remove_story_person(story_id: int, person_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    person_ids = [p.id for p in story.persons]
    try:
        index = person_ids.index(person_id)
        story.persons.pop(index)
        db.commit()
        db.refresh(story)
    except ValueError:
        pass
    return story


@router.put('/{story_id}/component/{component_id}', response_model=schemas.StoryBase)
async def add_story_component(story_id: int, component_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    component = await get_component_by_id(component_id, db)
    story.components.append(component)
    db.commit()
    db.refresh(story)
    return story


@router.delete('/{story_id}/component/{component_id}', response_model=schemas.StoryBase)
async def remove_story_component(story_id: int, component_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    component_ids = [c.id for c in story.components]
    try:
        index = component_ids.index(component_id)
        story.components.pop(index)
        db.commit()
        db.refresh(story)
    except ValueError:
        pass
    return story


@router.put('/{story_id}/epic-group/{epic_group_id}', response_model=schemas.StoryBase)
async def add_story_epic_group(story_id: int, epic_group_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    epic_group = await get_epic_group_by_id(epic_group_id, db)
    story.epic_groups.append(epic_group)
    db.commit()
    db.refresh(story)
    return story


@router.delete('/{story_id}/epic-group/{epic_group_id}', response_model=schemas.StoryBase)
async def remove_story_epic_group(story_id: int, epic_group_id: int,
                                  db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    epic_group_ids = [e.id for e in story.epic_groups]
    try:
        index = epic_group_ids.index(epic_group_id)
        story.epic_groups.pop(index)
        db.commit()
        db.refresh(story)
    except ValueError:
        pass
    return story


@router.put('/{story_id}/products/{product_id}', response_model=schemas.StoryBase)
async def add_story_product(story_id: int, product_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    product = await get_product_by_id(product_id, db)
    story.products.append(product)
    db.commit()
    db.refresh(story)
    return story


@router.delete('/{story_id}/products/{product_id}', response_model=schemas.StoryBase)
async def remove_story_product(story_id: int, product_id: int, db: Session = Depends(get_db)):
    story = await get_story_by_id(story_id, db)
    product_ids = [e.id for e in story.products]
    try:
        index = product_ids.index(product_id)
        story.products.pop(index)
        db.commit()
        db.refresh(story)
    except ValueError:
        pass
    return story
