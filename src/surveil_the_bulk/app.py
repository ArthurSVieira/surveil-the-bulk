from fastapi import FastAPI

from surveil_the_bulk.routes import (
    apiRouter,
    pageRouter,
)
from surveil_the_bulk.db import init_db

init_db()
app = FastAPI(title='Surveil The Bulk')
app.include_router(apiRouter)
app.include_router(pageRouter)

