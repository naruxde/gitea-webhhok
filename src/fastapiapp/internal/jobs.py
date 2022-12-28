# -*- coding: utf-8 -*-
"""Jobs of gitea pyhook."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from enum import Enum
from logging import getLogger
from os.path import dirname
from subprocess import Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from typing import TextIO, Union
from uuid import uuid4

log = getLogger()


class JobStates(Enum):
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class JobBase:
    """
    Base class to execute jobs.

    You have to override the job() function, to do your own work. All outputs
    are redirected into internal file buffer. You have to read the output
    buffer to get stdout and stderr of the job execution.
    """

    def __init__(self):
        self._id = str(uuid4())
        self._status = JobStates.READY
        self._th_worker = Thread()

        # Kind of IPC with a buffer of one line
        self._job_log = NamedTemporaryFile("w", prefix="pyhook_", buffering=1)

    def __del__(self):
        self._job_log.close()

    def _worker_target(self) -> None:
        """Save execute the overriden job function and redirect output."""
        try:
            self.job()
        except Exception as e:
            self._status = JobStates.FAILED
            log.exception(e)
            self._job_log.write(str(e))
            return

        self._job_log.flush()
        self._status = JobStates.SUCCESS

    def write_log(self, text: str) -> None:
        """Write to job log."""
        self._job_log.write(text)

    def open_logfile(self) -> TextIO:
        """Get a file object to read the job log."""
        return open(self._job_log.name)

    def start(self) -> None:
        """Start worker thread for this job."""
        if self._status is JobStates.RUNNING:
            raise RuntimeError("Job was started and is running")
        if self._status is not JobStates.READY:
            raise RuntimeError("Job can not be started twice")

        self._status = JobStates.RUNNING
        self._th_worker = Thread(target=self._worker_target)
        self._th_worker.start()

    def job(self) -> None:
        """Override function with your own job."""
        raise NotImplementedError

    def wait(self, timeout: Union[float, None] = None) -> None:
        """Wait for job execution finished."""
        self._th_worker.join(timeout)

    @property
    def id(self):
        """Get unique id of this job."""
        return self._id

    @property
    def status(self) -> JobStates:
        """Get status of job."""
        return self._status


class JobProcess(JobBase):
    """Run a process as job."""

    def __init__(self, cmd: str):
        self.cmd = cmd
        super().__init__()

    def job(self) -> None:
        """This will execute the given command."""
        lst_proc = self.cmd.split()
        process = Popen(
            lst_proc,
            cwd=dirname(lst_proc[0]) or "./",
            bufsize=0,
            stdout=self._job_log,
            stderr=self._job_log,
        )
        while True:
            exit_code = process.poll()
            if type(exit_code) == int:
                break
            try:
                process.wait(1.0)
            except TimeoutExpired:
                continue

        if exit_code:
            log.error(f"Error {exit_code} on process '{self.cmd}'")
        else:
            log.info(f"Successful executed process '{self.cmd}'")


class JobLongRun(JobBase):
    """Just for developing a task, which runs 60 seconds."""

    def job(self) -> None:
        for i in range(60):
            self.write_log(f"Loop {i} times\n")
            sleep(1.0)


if __name__ == '__main__':
    from selectors import DefaultSelector, EVENT_READ


    class DemoJob(JobBase):
        """Define new job class."""

        def job(self) -> None:
            self.write_log("Testjob")


    job = DemoJob()

    sel = DefaultSelector()
    sel.register(job.open_logfile(), EVENT_READ, print)

    job.start()
    print(f"Started {job.id}")

    while True:
        # Wait for read event of job output
        events = sel.select(1.0)
        if not events and job.status is not JobStates.RUNNING:
            # Job finished and not more log data to read
            break

        for key, mask in events:
            key.data("Joboutput:", key.fileobj.read())
