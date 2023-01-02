# -*- coding: utf-8 -*-
"""Git jobs."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from collections import namedtuple
from configparser import ConfigParser
from glob import glob
from os import makedirs
from os.path import basename, exists, join
from re import search
from shutil import move
from tempfile import TemporaryDirectory
from typing import Dict, List
from uuid import uuid4

from ..internal.jobs import JobBase
from ..settings import api_settings

BuildTask = namedtuple("BuildTask", ["branch", "command", "distro", "git_push"])


class GitBuildPackage(JobBase):

    def __init__(self, ssh_url: str, merge_version_tag: str,
                 build_tasks: List[BuildTask],
                 environment_variables: Dict[str, str] = None,
                 version_regex: str = None,
                 job_id: str = None,
                 ):
        """
        Create a build job for a version tag.

        The version will be captured from the tag name. The default is to
        start at the first number and use the rest of the name as version. You
        can change this behavior by setting a version_regex.

        :param ssh_url: Address to clone the repository
        :param merge_version_tag: Tag to merge into build branch
        :param build_tasks: Build the version vor each given task
        :param environment_variables: Append these variables into build environment
        :param version_regex: Regex to find version number in tag name
        :param job_id: Set own id for job
        """
        super().__init__(job_id)

        self.ssh_url = ssh_url
        self.merge_tag = merge_version_tag

        match = search(version_regex or r"[0-9].*", merge_version_tag)
        if not match:
            raise ValueError("Can not find version number with regex")
        self.version = match.group()

        self.build_tasks = build_tasks.copy()
        self.build_env = environment_variables.copy() if environment_variables else None

        makedirs(api_settings.save_package_dir, exist_ok=True)

    def job(self) -> None:
        def shell(cmd: str, cwd: str = None):
            if self.shell_exec(cmd, cwd or dir_repo, self.build_env):
                raise RuntimeError("Failed to clone repository")

        dir_job = TemporaryDirectory("build", "gitea")

        for build_task in self.build_tasks:  # type: BuildTask

            # Need new root for build in wich the packages are dropped
            dir_build = join(dir_job.name, str(uuid4()))
            # Git data will be cloned to this directory
            dir_repo = join(dir_build, "git_repo")
            makedirs(dir_repo)

            try:
                shell(f"git clone -b {build_task.branch} {self.ssh_url} {dir_repo}", dir_build)
                shell(f"git fetch --tags")
                shell(f"git merge {self.merge_tag} -m \"Merge '{self.merge_tag}' into {build_task.branch}\"")

                gbp_conf = ConfigParser()
                gpb_conf_file = join(dir_repo, "debian", "gbp.conf")
                if exists(gpb_conf_file):
                    gbp_conf.read(gpb_conf_file)

                pristine_tar = gbp_conf.getboolean("DEFAULT", "pristine-tar", fallback=False)
                if pristine_tar:
                    # Fetch pristine tar branch before building the package
                    shell(f"git checkout -t origin/pristine-tar")
                    shell(f"git fetch")
                    shell(f"git checkout {build_task.branch}")

                # Create debian changelog
                shell(
                    f"gbp dch -R"
                    f" -N {self.version}-1"
                    f" --distribution={build_task.distro}"
                    f" --commit"
                    f" --spawn-editor=never",
                )

                # Build package
                shell(f"gbp buildpackage --git-tag --git-pristine-tar-commit -us -uc")

                # Push the changes
                if build_task.git_push:
                    if pristine_tar:
                        shell(f"git push origin pristine-tar")
                    shell(f"git push origin {build_task.branch} pristine-tar")
                    shell(f"git push --tags origin")

                # Find package name by getting filename of .deb file
                deb_file = glob(join(dir_build, "*.deb"))
                if not deb_file:
                    raise RuntimeError("Could not verify build output - no debian package")

                # Get the generated package name with version number from .dcs file
                deb_directory = basename(deb_file[0]).strip(".deb")
                save_package_dir_test = join(api_settings.save_package_dir, deb_directory)
                save_package_dir = save_package_dir_test

                # Test existence of build dir and set suffix of _build2...n if exists
                suffix_counter = 1
                while exists(save_package_dir):
                    suffix_counter += 1
                    save_package_dir = f"{save_package_dir_test}_build{suffix_counter}"

                makedirs(save_package_dir)
                for file in glob(join(dir_build, f"*.*")):
                    move(file, save_package_dir)

            except RuntimeError:
                continue

        dir_job.cleanup()
