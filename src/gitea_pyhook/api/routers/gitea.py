# -*- coding: utf-8 -*-
"""Gitea webhook destination."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED

from .jobs import job_to_model
from ..dependencies import WebhookHeaders
from ..internal.database import get_build_env
from ..internal.gitjobs import BuildTask, GitBuildPackage
from ..internal.jobmgr import jobs
from ..models.gitea import GiteaWebhookPush, GiteaWebhookRef
from ..models.jobs import JobInformation

router = APIRouter(
    prefix="/gitea",
    tags=["webhook destination"],
    responses={
        400: {"description": "Wrong values for build job"},
    },
)


@router.post("/push/{build_environment}", response_model=JobInformation, status_code=HTTP_201_CREATED)
async def gitea_push(build_environment: str,
                     push: GiteaWebhookPush,
                     gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """
    Entry point for gitea push.

    Something was deleted, if "after" is "0000000000000000000000000000000000000000".
    """
    data = JobInformation(
        job_id=0,
        href="/jobs/0",
        status="failed",
        href_ws="/jobs/0/ws",
        msg="not implemented jet"
    )
    return data


@router.post("/ref/{build_environment}", response_model=JobInformation, status_code=HTTP_201_CREATED)
async def gitea_ref(build_environment: str,
                    ref: GiteaWebhookRef,
                    gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea tag creation."""
    if not ref.ref_type == "tag":
        raise HTTPException(400, "The ref type must be tag")

    build_environment = await get_build_env(build_environment)
    if not build_environment:
        raise HTTPException(404, "Can not find build environment")

    dc_environment = {}
    for variables in build_environment.environment_variables:
        dc_environment[variables.name] = variables.value

    lst_build_tasks = []
    for task in build_environment.build_options:
        lst_build_tasks.append(BuildTask(
            task.branch,
            task.command,
            task.distro
        ))

    build_job = GitBuildPackage(
        ref.repository.ssh_url,
        f"refs/tags/{ref.ref}",
        lst_build_tasks,
        dc_environment,
    )
    jobs[build_job.id] = build_job

    build_job.start()

    return job_to_model(build_job)
