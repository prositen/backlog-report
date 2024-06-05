from typing import Optional, List

from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ReportBase
from app.db.schemas import ReportFieldBase, ReportField
from app.routers.admin.shortcut import get_db


class Crud(object):

    def __init__(self, item_model: type[ReportBase], name: str,
                 schema_model: Optional[type[ReportFieldBase]] = None):
        self.item_model = item_model
        self.name = name
        self.schema_model = schema_model

    async def create_item(self, item: ReportFieldBase, db: Session = Depends(get_db)):
        query = select(self.item_model).where(self.item_model.name == item.name)
        if db.execute(query).first():
            raise HTTPException(status_code=400, detail=f"{self.name} already exists")

        db_item = self.item_model(name=item.name)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    async def get_items(self, db: Session = Depends(get_db)):
        query = select(self.item_model)
        x = db.execute(query).scalars()
        return x

    async def get_item_by_id(self, item_id, db: Session = Depends(get_db)):
        query = select(self.item_model).where(self.item_model.id == item_id)
        if item := db.execute(query).scalar_one_or_none():
            return item
        raise HTTPException(404, detail=f"{self.name} not found")

    async def update_item_by_id(self, item_id: int, item: ReportField,
                                db: Session = Depends(get_db)):
        query = select(self.item_model).where(self.item_model.id == item_id)
        if db_item := db.execute(query).scalar_one_or_none():
            item.id = item_id
            update_item = self.item_model(**item.dict())
            db.merge(update_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        raise HTTPException(404, detail=f"{self.name} not found")

    async def delete_item_by_id(self, item_id: int, db: Session = Depends(get_db)):
        query = select(self.item_model).where(self.item_model.id == item_id)
        if db_item := db.execute(query).scalar_one_or_none():
            db.delete(db_item)
            db.commit()
            return {'message': f'Deleted {db_item.name} successfully'}
        raise HTTPException(404, detail=f"{self.name} not found")

    def add_routes(self, router: APIRouter):
        router.add_api_route(path='',
                             endpoint=self.get_items, methods=['GET'],
                             response_model=List[self.schema_model])
        router.add_api_route(path='',
                             endpoint=self.create_item, methods=['POST'],
                             response_model=self.schema_model)
        router.add_api_route(path='/{item_id}',
                             endpoint=self.get_item_by_id, methods=['GET'],
                             response_model=self.schema_model)
        router.add_api_route(path='/{item_id}',
                             endpoint=self.update_item_by_id, methods=['PUT'],
                             response_model=self.schema_model)
        router.add_api_route(path='/{item_id}',
                             endpoint=self.delete_item_by_id, methods=['DELETE'])
