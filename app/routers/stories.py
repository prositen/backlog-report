from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import schemas, models
from app.routers.admin.shortcut import get_db
from app.routers.persons import get_person_by_id

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
    person = get_person_by_id(person_id, db)
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
