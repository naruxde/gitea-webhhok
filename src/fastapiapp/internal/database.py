# -*- coding: utf-8 -*-
"""Database manager."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2022 Sven Sager"
__license__ = "GPLv3"

from sqlite3 import Row
from typing import Union

import aiosqlite
from aiosqlite import Connection, Cursor

from fastapiapp.models.envs import BuildEnvironment, BuildOptions, EnvironmentVariables

sql_db = None  # type: Connection


async def connect():
    global sql_db
    sql_db = await aiosqlite.connect("db/gitea-pyhook.db")
    sql_db.row_factory = Row


async def disconnect():
    await sql_db.close()


async def get_build_env(build_envs_name: str) -> Union[BuildEnvironment, None]:
    cur = await sql_db.execute("SELECT * FROM build_envs WHERE name=?", (build_envs_name,))  # type: Cursor
    row = await cur.fetchone()
    if not row:
        return

    cur_variables = await sql_db.execute("SELECT * FROM env_variables WHERE fk_build_envs=?", (row["id"],))
    cur_options = await sql_db.execute("SELECT * FROM build_options WHERE fk_build_envs=?", (row["id"],))

    return BuildEnvironment(
        name=row["name"],
        environment_variables=[EnvironmentVariables(
            name=row["name"],
            value=row["value"],
        ) for row in await cur_variables.fetchall()],
        build_options=[BuildOptions(
            branch=row["branch"],
            command=row["command"],
            distro=row["distro"],
        ) for row in await cur_options.fetchall()],
    )


async def get_build_env_all() -> list:
    cur = await sql_db.execute("SELECT name FROM build_envs")  # type: Cursor
    tb = await cur.fetchall()
    return [await get_build_env(row["name"]) for row in tb if row]
