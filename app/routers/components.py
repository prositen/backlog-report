from fastapi import APIRouter

from app.db import schemas, models
from app.db.crud import Crud

router = APIRouter(prefix='/components',
                   tags=['components'],
                   responses={404: {"description": "Not found"}}
                   )

component_crud = Crud(models.Component, 'Component',
                      schema_model=schemas.Component)

component_crud.add_routes(router)

get_component_by_id = component_crud.get_item_by_id
