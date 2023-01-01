# -*- coding: utf-8 -*-
"""Data models of gitea resource."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2023 Sven Sager"
__license__ = "GPLv3"

from datetime import datetime
from typing import Any, List, Union

from pydantic import BaseModel, HttpUrl

from .common import SimpleUserInfo


class GiteaCommit(BaseModel):
    id: str
    message: str
    url: HttpUrl
    author: SimpleUserInfo
    committer: SimpleUserInfo
    verification: Any
    timestamp: datetime
    added: List[str]
    removed: List[str]
    modified: List[str]


class GiteaUser(BaseModel):
    id: int
    login: str
    full_name: str
    email: str
    avatar_url: Union[HttpUrl, str]
    language: str
    is_admin: bool
    last_login: datetime
    created: datetime
    restricted: bool
    active: bool
    prohibit_login: bool
    location: str
    website: Union[HttpUrl, str]
    description: str
    visibility: str
    followers_count: int
    following_count: int
    starred_repos_count: int
    username: str


class GiteaRepository(BaseModel):
    class GiteaInternalTracker(BaseModel):
        enable_time_tracker: bool
        allow_only_contributors_to_track_time: bool
        enable_issue_dependencies: bool

    class GiteaPermissions(BaseModel):
        admin: bool
        push: bool
        pull: bool

    id: int
    owner: GiteaUser
    name: str
    full_name: str
    description: str
    empty: bool
    private: bool
    fork: bool
    template: bool
    # parent: # todo: Find out data
    mirror: bool
    size: int
    language: str
    languages_url: HttpUrl
    html_url: HttpUrl
    ssh_url: str
    clone_url: HttpUrl
    original_url: Union[HttpUrl, str]
    website: Union[HttpUrl, str]
    stars_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    open_pr_counter: int
    release_counter: int
    default_branch: str
    archived: bool
    created_at: datetime
    updated_at: datetime
    permissions: GiteaPermissions
    has_issues: bool
    internal_tracker: GiteaInternalTracker
    has_wiki: bool
    has_pull_requests: bool
    has_projects: bool
    ignore_whitespace_conflicts: bool
    allow_merge_commits: bool
    allow_rebase: bool
    allow_rebase_explicit: bool
    allow_squash_merge: bool
    default_merge_style: str
    avatar_url: Union[HttpUrl, str]
    internal: bool
    mirror_interval: str
    mirror_updated: datetime
    # repo_transfer: # todo: Find out data


class GiteaWebhookPush(BaseModel):
    """
    Describes the push object.

    This will be used for pushed commits, incl. new branches, tags and so on.
    """
    ref: str
    before: str
    after: str
    compare_url: HttpUrl
    commits: List[GiteaCommit]
    total_commits: int
    head_commit: Union[GiteaCommit, None]
    repository: GiteaRepository
    pusher: GiteaUser
    sender: GiteaUser

    def __str__(self):
        return f"{self.ref}_{self.repository.name}"


class GiteaWebhookRef(BaseModel):
    """
    Describes a ref object.

    This will be used for create or delete tags and branches.
    """
    sha: str = ""
    ref: str
    ref_type: str
    pusher_type: str = ""
    repository: GiteaRepository
    sender: GiteaUser

    def __str__(self):
        return f"{self.ref_type}_{self.repository.name}"
