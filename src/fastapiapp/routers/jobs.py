# -*- coding: utf-8 -*-
"""Job history of webhook actions."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

import asyncio

from fastapi import APIRouter
from starlette.websockets import WebSocket

from .. import JobBase, jobs
from ..internal.jobs import JobLongRun, JobStates

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)


def job_to_json(job: JobBase) -> dict:
    return {
        "job_id": job.id,
        "status": job.status,
        "href": f"/jobs/{job.id}",
        "websocket": f"/jobs/{job.id}/ws",
    }


@router.get("/")
async def read_jobs():
    lst_jobs = [job_to_json(job) for job in jobs.values()]
    return lst_jobs


@router.get("/{job_id}")
async def read_job(job_id: str):
    return job_to_json(jobs[job_id])


@router.post("/")
async def test_job():
    """Testjob with autostart."""
    job = JobLongRun()
    jobs[job.id] = job
    job.start()
    return job_to_json(job)


@router.websocket("/{job_id}/ws")
async def job_websocket(ws: WebSocket, job_id: str):
    job = jobs[job_id]
    await ws.accept()

    while True:
        data = job.output.read()
        if not data:
            if job.status is not JobStates.RUNNING:
                break
            await asyncio.sleep(0.1)
            continue
        await ws.send_text(data)

    await ws.close()
