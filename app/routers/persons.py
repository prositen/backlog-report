from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import schemas, models
from app.routers.admin.shortcut import get_db

router = APIRouter(prefix='/persons', tags=['persons'])


@router.post('', response_model=schemas.Person)
async def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    query = select(models.Person).where(models.Person.name == person.name)
    if db.execute(query).first():
        raise HTTPException(status_code=400, detail="Person already exists")
    db_person = models.Person(name=person.name)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.get('', response_model=List[schemas.Person])
async def get_persons(db: Session = Depends(get_db)):
    query = select(models.Person)
    return db.execute(query).scalars()


@router.get('/{person_id}', response_model=schemas.Person)
async def get_person_by_id(person_id: int, db: Session = Depends(get_db)):
    query = select(models.Person).where(models.Person.id == person_id)
    if person := db.execute(query).scalar_one_or_none():
        return person
    raise HTTPException(404, detail="Person not found")


@router.post('/{person_id}', response_model=schemas.Person)
async def update_person_by_id(person_id: int, person: schemas.Person,
                              db: Session = Depends(get_db)):
    query = select(models.Person).where(models.Person.id == person_id)
    if db_person := db.execute(query).scalar_one_or_none():
        person.id = person_id
        update_person = models.Person(**person.dict())
        db.merge(update_person)
        db.commit()
        db.refresh(db_person)
        return db_person
    raise HTTPException(404, detail="Person not found")


@router.delete('/{person_id}')
async def delete_person_by_id(person_id: int, db: Session = Depends(get_db)):
    query = select(models.Person).where(models.Person.id == person_id)
    if db_person := db.execute(query).scalar_one_or_none():
        db.delete(db_person)
        db.commit()
        return {'message': f'Deleted {db_person.name} successfully'}
    raise HTTPException(404, detail="Person not found")
