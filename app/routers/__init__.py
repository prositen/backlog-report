from .admin import shortcut as admin_shortcut
from . import shortcut, persons, stories, components


def api_router():
    from fastapi.routing import APIRouter
    router = APIRouter()
    router.include_router(shortcut.router)
    router.include_router(admin_shortcut.router)
    router.include_router(persons.router)
    router.include_router(stories.router)
    router.include_router(components.router)
    return router
