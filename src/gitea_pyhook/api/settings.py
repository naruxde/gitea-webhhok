# -*- coding: utf-8 -*-
"""Settings of api."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"


class Settings:
    """Manage global settings of api."""

    def __init__(self):
        self.save_package_dir = "/tmp/gitea-pyhook"
        self.sqlite_file = "./db/gitea-pyhook.db"


api_settings = Settings()
