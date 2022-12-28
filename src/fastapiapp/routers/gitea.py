# -*- coding: utf-8 -*-
"""Gitea webhook destination."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import APIRouter, Depends

from ..dependencies import WebhookHeaders
from ..models.gitea import GiteaWebhookPush, GiteaWebhookTag
from ..models.jobs import JobInformation

router = APIRouter(
    prefix="/gitea",
    tags=["webhook destination"],
    responses={404: {"description": "Not found"}},
)


@router.post("/push", response_model=JobInformation)
async def gitea_post(hook: GiteaWebhookPush, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea webhook."""
    data = JobInformation(
        job_id=0,
        href="/jobs/0",
        status="not jet implemented",
        webhook="/jobs/0/ws",
    )
    return data


@router.post("/tag", response_model=JobInformation)
async def gitea_post(hook: GiteaWebhookTag, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea webhook."""
    data = JobInformation(
        job_id=0,
        href="/jobs/0",
        status="not jet implemented",
        webhook="/jobs/0/ws",
    )
    return data
