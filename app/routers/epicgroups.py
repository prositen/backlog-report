from fastapi import APIRouter

from app.db import schemas, models
from app.db.crud import Crud

router = APIRouter(prefix='/epic-groups',
                   tags=['epic groups'],
                   responses={404: {"description": "Not found"}}
                   )

epic_group_crud = Crud(models.EpicGroup, 'Epic group',
                       schema_model=schemas.EpicGroup)
epic_group_crud.add_routes(router)

get_epic_group_by_id = epic_group_crud.get_item_by_id
