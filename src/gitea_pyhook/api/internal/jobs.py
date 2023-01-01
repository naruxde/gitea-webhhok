# -*- coding: utf-8 -*-
"""Jobs of gitea pyhook."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from collections import namedtuple
from enum import Enum
from logging import getLogger
from subprocess import Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from typing import List, TextIO, Tuple, Union
from uuid import uuid4

log = getLogger()

ShellOutput = namedtuple("ShellOutput", ["cmd", "exit_code", "output"])


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

    def __init__(self, job_id: str = None):
        """Base class for all jobs."""
        self._id = job_id or str(uuid4())
        self._status = JobStates.READY
        self._th_worker = Thread()

        self._last_shell_output = ""

        # Kind of IPC with a buffer of one line
        self._job_log = NamedTemporaryFile("w+", prefix="pyhook_", buffering=1)

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

    def log_print(self, *objects, sep=" ", end="\n") -> None:
        """Write via print like implementation into job log."""
        print(*objects, sep=sep, end=end, file=self._job_log, flush=True)

    def log_write(self, text: str) -> None:
        """Write directly into job log."""
        self._job_log.write(text)

    def open_logfile(self) -> TextIO:
        """Get a file object to read the job log."""
        return open(self._job_log.name)

    def shell_exec(self, cmd: str, cwd: str = None, env: dict = None, timeout: float = None) -> int:
        """
        Execute the given command as subprocess.

        :param cmd: Command line to execute
        :param cwd: Change working directory
        :param env: Dictionary with additional environment variables
        :param timeout: Timeout in seconds of process
        :return: exit code of command or -1 on timed out
        """
        file_position = self._job_log.tell()

        process = Popen(
            cmd,
            bufsize=0,
            stdout=self._job_log,
            stderr=self._job_log,
            close_fds=False,
            shell=True,
            cwd=cwd,
            env=env,
        )
        try:
            exit_code = process.wait(timeout)
        except TimeoutExpired:
            return -1

        # Read job log just for the actual process execution
        self._job_log.seek(file_position)
        self._last_shell_output = self._job_log.read()

        return exit_code

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
    def last_shell_output(self) -> str:
        """Get the output from the last running shell_exec call."""
        return self._last_shell_output

    @property
    def running(self) -> bool:
        """Get running status of job."""
        return self._th_worker.is_alive()

    @property
    def status(self) -> JobStates:
        """Get status of job."""
        return self._status


class JobProcess(JobBase):
    """Run a process as job."""

    def __init__(self, cmd: Union[str, List[str]],
                 cwd: str = None, env: dict = None, stop_on_fail=True,
                 job_id: str = None):
        """
        Create a job based on external programs.

        If you pass a command list, the commands will be executed one by one.

        :param cmd: Single command or command list to execute
        :param cwd: Change working directory for all commands
        :param env: Dictionary with additional environment variables
        :param stop_on_fail: Stop working, if a command return an error
        :param job_id: Set own id for job
        """
        super().__init__(job_id)
        if type(cmd) == str:
            cmd = [cmd]
        self._cmd = cmd.copy()  # type: List[str]
        self._cwd = cwd
        self._env = env.copy() if env else {}
        self._stop_on_fail = stop_on_fail

        self._all_shell_outputs = []  # type: List[Tuple[str, int, str]]

    def job(self) -> None:
        """This will execute the given command."""
        for cmd in self._cmd:
            exit_code = self.shell_exec(cmd, self._cwd, self._env)
            self._all_shell_outputs.append(ShellOutput(cmd, exit_code, self.last_shell_output))
            if exit_code == 0:
                log.info(f"Successful executed process '{cmd}'")
            else:
                log.error(f"Error {exit_code} on process '{cmd}'")
                if self._stop_on_fail:
                    break

    @property
    def all_shell_outputs(self) -> List[Tuple[str, int, str]]:
        """
        Get a list of all shell executed processes.

        The output is a list with namedtuple, which contains the command, the
        exitcode and the output.
        """
        return self._all_shell_outputs.copy()

    @property
    def cmd(self) -> List[str]:
        """Get the command list."""
        return self._cmd.copy()

    @property
    def cwd(self) -> str:
        """Get working directory for all commands."""
        return self._cwd


class JobWaitAndPrint(JobBase):
    """Demo to build your own jobs by inheriting the JobBase class"""

    def __init__(self, runtime=60, job_id: str = None):
        """
        Run this job to print a log line every second.

        :param runtime: Seconds to run this job
        :param job_id: Set own id for job
        """
        self.runtime = runtime
        super().__init__(job_id)

    def job(self) -> None:
        """This is called from base class and handles exceptions."""
        for i in range(1, self.runtime + 1):
            self.log_print(f"Loop {i} times\n")
            sleep(1.0)


if __name__ == '__main__':
    from selectors import DefaultSelector, EVENT_READ

    lst_jobs = [
        JobProcess([
            "ls",
            "find ./ -name '*.py'",
            "pwd",
        ]),
        JobWaitAndPrint(10),
    ]

    sel = DefaultSelector()
    for job in lst_jobs:
        logfile = job.open_logfile()
        sel.register(logfile, EVENT_READ)

        job.start()
        print(f"Started {job.id}")

        while True:
            # Wait for read event of job output
            events = sel.select(1.0)
            if not events and job.status is not JobStates.RUNNING:
                # Job finished and not more log data to read
                break

            for key, mask in events:
                print("Job output:", logfile.read(), end="")

        if isinstance(job, JobProcess):
            print("Shell output", job.all_shell_outputs)

        sel.unregister(logfile)
        logfile.close()
