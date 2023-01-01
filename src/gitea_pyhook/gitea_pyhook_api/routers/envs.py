# -*- coding: utf-8 -*-
"""Environment resource."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from logging import getLogger
from typing import List

from fastapi import APIRouter, HTTPException

from ..internal.database import get_build_env, get_build_env_all
from ..models.envs import BuildEnvironment

log = getLogger()

router = APIRouter(
    prefix="/envs",
    tags=["environments"],
    responses={404: {"description": "Environment not found"}},
)


@router.get("/", response_model=List[BuildEnvironment])
async def read_envs():
    lst = await get_build_env_all()
    return lst


@router.get("/{name}", response_model=BuildEnvironment)
async def get_env_by_name(name: str):
    environment = await get_build_env(name)
    if not environment:
        raise HTTPException(404, "Can not find build environment")
    return environment
