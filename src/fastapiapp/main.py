# -*- coding: utf-8 -*-
"""FastAPI server of gitea pyhook."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import FastAPI

from . import __version__
from . import routers
from .internal import database

app = FastAPI(
    title="Build manager for gitea webhooks.",
    version=__version__,
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(routers.envs.router)
app.include_router(routers.gitea.router)
app.include_router(routers.jobs.router)
