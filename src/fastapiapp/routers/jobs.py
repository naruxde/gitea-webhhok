# -*- coding: utf-8 -*-
"""Job history of webhook actions."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

import asyncio
from typing import List

from fastapi import APIRouter, HTTPException
from starlette.websockets import WebSocket

from .. import JobBase, jobs
from ..internal.jobs import JobLongRun, JobStates
from ..models.jobs import JobInformation

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Job not found"}},
)


def job_to_model(job: JobBase) -> JobInformation:
    data = JobInformation(
        job_id=job.id,
        status=job.status.value,
        href=f"/jobs/{job.id}",
        href_ws=f"/jobs/{job.id}/ws",
    )
    return data


@router.get("/", response_model=List[JobInformation])
async def read_jobs():
    lst_jobs = [job_to_model(job) for job in jobs.values()]
    return lst_jobs


@router.get("/{job_id}", response_model=JobInformation)
async def read_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return job_to_model(jobs[job_id])


@router.post("/", response_model=JobInformation)
async def test_job():
    """Testjob with autostart."""
    job = JobLongRun()
    jobs[job.id] = job
    job.start()
    return job_to_model(job)


@router.websocket("/{job_id}/ws")
async def job_websocket(ws: WebSocket, job_id: str):
    await ws.accept()
    if job_id not in jobs:
        ex = HTTPException(404, "Job not found")
        await ws.send_text(f"{ex.status_code}: {ex.detail}")
        await ws.close()
        raise ex

    job = jobs[job_id]
    log_file = job.open_logfile()

    while True:
        data = log_file.read()
        if not data:
            if job.status is not JobStates.RUNNING:
                break
            await asyncio.sleep(0.1)
            continue
        await ws.send_text(data)

    await ws.close()
