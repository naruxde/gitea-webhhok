# -*- coding: utf-8 -*-
"""Data models for job resource."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from pydantic import BaseModel, HttpUrl

from fastapiapp.internal.jobs import JobStates


class JobInformation(BaseModel):
    """Common job object"""

    job_id: str
    href: str
    status: JobStates
    webhook: str
