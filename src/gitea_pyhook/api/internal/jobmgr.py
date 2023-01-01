# -*- coding: utf-8 -*-
"""Job manager to handle all jobs."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from typing import Dict

from .jobs import JobBase

# fixme: We need some kind of database
jobs = {}  # type: Dict[str, JobBase]
