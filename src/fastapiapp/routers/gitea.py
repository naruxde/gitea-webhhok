# -*- coding: utf-8 -*-
"""Gitea webhook destination."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import APIRouter, Depends

from ..dependencies import WebhookHeaders
from ..models.gitea import GiteaWebhookPush, GiteaWebhookRef
from ..models.jobs import JobInformation

router = APIRouter(
    prefix="/gitea",
    tags=["webhook destination"],
    responses={404: {"description": "Not found"}},
)


@router.post("/push", response_model=JobInformation)
async def gitea_push(push: GiteaWebhookPush, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
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


@router.post("/ref", response_model=JobInformation)
async def gitea_ref(hook: GiteaWebhookRef, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea webhook."""
    data = JobInformation(
        job_id=0,
        href="/jobs/0",
        status="failed",
        href_ws="/jobs/0/ws",
        msg="not implemented jet"
    )
    return data
