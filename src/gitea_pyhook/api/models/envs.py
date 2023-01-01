# -*- coding: utf-8 -*-
"""Data models for envs resource."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from typing import List

from pydantic import BaseModel


class BuildOptions(BaseModel):
    """Build options."""
    branch: str
    command: str
    distro: str


class EnvironmentVariables(BaseModel):
    """Variables for build environment."""
    name: str
    value: str


class BuildEnvironment(BaseModel):
    """Build environment object"""

    name: str
    environment_variables: List[EnvironmentVariables] = []
    build_options: List[BuildOptions] = []
