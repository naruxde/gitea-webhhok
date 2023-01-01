# -*- coding: utf-8 -*-
"""Common used data models for all resources."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from pydantic import BaseModel


class SimpleUserInfo(BaseModel):
    name: str
    email: str
    username: str
