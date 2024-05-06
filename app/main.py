from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from .routers import api_router
from .core.config import Config
import logging
import sys

app = FastAPI(
    title="shortcut-report",
    version=Config.get_config().version
)

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)
app.include_router(api_router())

logger = logging.getLogger(__name__)

access_handler = logging.StreamHandler(stream=sys.stdout)
access_handler.setFormatter(logging.Formatter("%(levelname)s \t %(message)s"))

logger.handlers = [access_handler]

logger.setLevel(Config.get_config().log_level)


@app.get("/")
@app.get("/version")
def index():
    logger.debug(__name__)

    return {"name": app.title, "version": Config.get_config().version}

