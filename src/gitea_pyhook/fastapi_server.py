# -*- coding: utf-8 -*-
"""Uvicorn manager to run our fastapi application."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from logging import getLogger
from threading import Thread

import uvicorn

from . import api

log = getLogger()


class FastApiServer(Thread):
    """
    Run asyncio fastapi application in a new thread.

    This thread will start the uvicorn server to serve our fast api app. The
    stop() function will shut down the server. Signal handlers are not
    installed by uvicorn.
    """

    def __init__(self, host="127.0.0.1", port=8000):
        super().__init__()
        self._config = uvicorn.Config(
            api.app,
            host=host,
            port=port,
        )
        self._server = uvicorn.Server(self._config)

    def run(self) -> None:
        log.debug("Enter FastApiServer.run")
        self._server.run()
        log.debug("Leave FastApiServer.run")

    def stop(self) -> None:
        """Shutdown the uvicorn server."""
        log.debug("Enter FastApiServer.stop")

        if not self._server.started:
            return

        self._server.should_exit = True
        self.join(5.0)
        if self.is_alive():
            log.error("Could not stop uvicorn server")

        log.debug("Leave FastApiServer.stop")


if __name__ == '__main__':
    fas = FastApiServer()

    # Do not start thread, just the uvicorn server
    fas.run()
