from fastapi import APIRouter

from app.db import schemas, models
from app.db.crud import Crud

router = APIRouter(prefix='/products',
                   tags=['products'],
                   responses={404: {"description": "Not found"}}
                   )

product_crud = Crud(models.Product, 'Product',
                    schema_model=schemas.Product)
product_crud.add_routes(router)

get_product_by_id = product_crud.get_item_by_id
