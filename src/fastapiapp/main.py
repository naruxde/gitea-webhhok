# -*- coding: utf-8 -*-
"""FastAPI server of gitea pyhook."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import FastAPI

from . import __version__
from . import routers

app = FastAPI(
    version=__version__,
)

app.include_router(routers.gitea.router)
app.include_router(routers.jobs.router)
