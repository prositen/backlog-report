from fastapi import APIRouter

from app.db import schemas, models
from app.db.crud import Crud

router = APIRouter(prefix='/persons',
                   tags=['persons'],
                   responses={404: {"description": "Not found"}}
                   )

person_crud = Crud(item_model=models.Person, name='Person',
                   schema_model=schemas.Person)
person_crud.add_routes(router)

get_person_by_id = person_crud.get_item_by_id
