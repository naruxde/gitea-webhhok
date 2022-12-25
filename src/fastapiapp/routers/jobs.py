# -*- coding: utf-8 -*-
"""Job history of webhook actions."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import APIRouter

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def read_jobs():
    return [{
        "jobid": "0",
        "status": "Not jet implemented"
    }]


@router.get("/{job_id}")
async def read_job(job_id: str):
    return {
        "jobid": job_id,
        "status": "Not jet implemented"
    }
