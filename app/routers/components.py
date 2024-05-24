from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import schemas, models
from app.routers.admin.shortcut import get_db

router = APIRouter(prefix='/components', tags=['components'])


@router.post('', response_model=schemas.Component)
def create_component(component: schemas.ComponentCreate, db: Session = Depends(get_db)):
    query = select(models.Component).where(models.Component.name == component.name)
    if db.execute(query).first():
        raise HTTPException(status_code=400, detail="Component already exists")
    db_component = models.Component(name=component.name)
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


@router.get('', response_model=List[schemas.Component])
def get_components(db: Session = Depends(get_db)):
    query = select(models.Component)
    return db.execute(query).scalars()


@router.get('/{component_id}', response_model=schemas.Component)
def get_component_by_id(component_id: int, db: Session = Depends(get_db)):
    query = select(models.Component).where(models.Component.id == component_id)
    if component := db.execute(query).scalar_one_or_none():
        return component
    raise HTTPException(404, detail="Component not found")


@router.post('/{component_id}', response_model=schemas.Component)
def update_component_by_id(component_id: int, component: schemas.Component,
                           db: Session = Depends(get_db)):
    query = select(models.Component).where(models.Component.id == component_id)
    if db_component := db.execute(query).scalar_one_or_none():
        component.id = component_id
        update_component = models.Component(**component.dict())
        db.merge(update_component)
        db.commit()
        db.refresh(db_component)
        return db_component
    raise HTTPException(404, detail="Component not found")
