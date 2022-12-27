# -*- coding: utf-8 -*-
"""Package of gitea pyhook."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"
__version__ = "0.1.0"

from typing import Dict

from fastapiapp.internal.jobs import JobBase

# fixme: We need some kind of database
jobs = {}  # type: Dict[str, JobBase]

from .main import app
