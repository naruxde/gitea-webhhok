# -*- coding: utf-8 -*-
"""Dependencies for resources of FastAPI endpoints."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from typing import Union

from fastapi import HTTPException, Header


class WebhookHeaders:
    """Values of gitea headers."""

    def __init__(
            self,
            x_gitea_delivery: Union[str, None] = Header(default=None),
            x_gitea_event: Union[str, None] = Header(default=None),
            x_gitea_event_type: Union[str, None] = Header(default=None),
            x_gitea_signature: Union[str, None] = Header(default=None)):
        if not (x_gitea_delivery, x_gitea_event, x_gitea_event_type, x_gitea_signature):
            raise HTTPException(400, "Missing gitea headers")

        self.delivery = x_gitea_delivery
        self.event = x_gitea_event
        self.event_type = x_gitea_event_type
        self.signature = x_gitea_signature
