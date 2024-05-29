from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import schemas, models
from app.routers.admin.shortcut import get_db

router = APIRouter(prefix='/epic-groups', tags=['epic groups'])


def get_epic_group(epic_group_id: int, db: Session = Depends(get_db)):
    query = select(models.EpicGroup).where(models.EpicGroup.id == epic_group_id)
    return db.execute(query).scalar_one_or_none()


@router.post('', response_model=schemas.Person)
async def create_epic_group(epic_group: schemas.EpicGroupCreate, db: Session = Depends(get_db)):
    query = select(models.EpicGroup).where(models.EpicGroup.name == epic_group.name)
    if db.execute(query).first():
        raise HTTPException(status_code=400, detail="Epic group already exists")
    db_epic_group = models.EpicGroup(name=epic_group.name)
    db.add(db_epic_group)
    db.commit()
    db.refresh(db_epic_group)
    return db_epic_group


@router.get('', response_model=List[schemas.EpicGroup])
async def get_epic_groups(db: Session = Depends(get_db)):
    query = select(models.EpicGroup)
    return db.execute(query).scalars()


@router.get('/{epic_group_id}', response_model=schemas.EpicGroup)
async def get_epic_group_by_id(epic_group_id: int, db: Session = Depends(get_db)):
    query = select(models.EpicGroup).where(models.EpicGroup.id == epic_group_id)
    if epic_group := db.execute(query).scalar_one_or_none():
        return epic_group
    raise HTTPException(404, detail="Epic group not found")


@router.post('/{epic_group_id}', response_model=schemas.EpicGroup)
async def update_person_by_id(epic_group_id: int, epic_group: schemas.EpicGroup,
                              db: Session = Depends(get_db)):
    if db_epic_group := get_epic_group(epic_group_id, db):
        epic_group.id = epic_group_id
        update_person = models.Person(**epic_group.dict())
        db.merge(update_person)
        db.commit()
        db.refresh(db_epic_group)
        return db_epic_group
    raise HTTPException(404, detail="Epic group not found")


@router.delete('/{epic_group_id}')
async def delete_epic_group_by_id(epic_group_id: int, db: Session = Depends(get_db)):
    if db_epic_group := get_epic_group(epic_group_id, db):
        db.delete(db_epic_group)
        db.commit()
        return {'message': f'Deleted {db_epic_group.name} successfully'}
    raise HTTPException(404, detail="Epic group not found")
