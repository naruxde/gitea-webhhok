# -*- coding: utf-8 -*-
"""Gitea webhook destination."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from fastapi import APIRouter, Depends

from ..dependencies import WebhookHeaders
from ..models import ModelGiteaWebhookPush, ModelGiteaWebhookTag

router = APIRouter(
    prefix="/gitea",
    tags=["webhook destination"],
    responses={404: {"description": "Not found"}},
)


@router.post("/push")
async def gitea_post(hook: ModelGiteaWebhookPush, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea webhook."""
    return {
        "jobid": "0",
        "href": "/jobs/0",
        "status": "not jet implemented",
        "headers": {
            "event": gt_headers.event,
            "delivery": gt_headers.delivery,
        }
    }


@router.post("/tag")
async def gitea_post(hook: ModelGiteaWebhookTag, gt_headers: WebhookHeaders = Depends(WebhookHeaders)):
    """Entry point for gitea webhook."""
    return {
        "jobid": "0",
        "href": "/jobs/0",
        "status": "not jet implemented",
        "headers": {
            "event": gt_headers.event,
            "delivery": gt_headers.delivery,
        }
    }
