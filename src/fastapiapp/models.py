# -*- coding: utf-8 -*-
"""Data models of this API."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from datetime import datetime
from typing import Any, List, Union

from pydantic import BaseModel, HttpUrl


class ModelUserInfo(BaseModel):
    name: str
    email: str
    username: str


class ModelCommit(BaseModel):
    id: str
    message: str
    url: HttpUrl
    author: ModelUserInfo
    committer: ModelUserInfo
    verification: Any
    timestamp: datetime
    added: List[str]
    removed: List[str]
    modified: List[str]


class ModelGiteaUser(BaseModel):
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


class ModelRepository(BaseModel):
    class ModelInternalTracker(BaseModel):
        enable_time_tracker: bool
        allow_only_contributors_to_track_time: bool
        enable_issue_dependencies: bool

    class ModelPermissions(BaseModel):
        admin: bool
        push: bool
        pull: bool

    id: int
    owner: ModelGiteaUser
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
    permissions: ModelPermissions
    has_issues: bool
    internal_tracker: ModelInternalTracker
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


class ModelGiteaWebhookPush(BaseModel):
    """Describes the push webhook object."""
    ref: str
    before: str
    after: str
    compare_url: HttpUrl
    commits: List[ModelCommit]
    total_commits: int
    head_commit: ModelCommit
    repository: ModelRepository
    pusher: ModelGiteaUser
    sender: ModelGiteaUser


class ModelGiteaWebhookTag(BaseModel):
    """Describes the tag webhook object."""
    sha: str = ""
    ref: str
    ref_type: str
    pusher_type: str = ""
    repository: ModelRepository
    sender: ModelGiteaUser
