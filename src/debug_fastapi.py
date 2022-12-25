# -*- coding: utf-8 -*-
"""Debug fast api app with python debugging tools."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

import uvicorn

import fastapiapp

uvicorn.run(fastapiapp.app)
