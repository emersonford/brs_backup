#!/usr/bin/env python3

import os
from typing import List, Dict, Optional

import mysql.connector
import bareos.bsock
from git import Repo

import logger
import config
import secrets

LOGGER = logger.get_logger(__name__)


def write_job_file(
    name: str,
    fileset: str,
    client: str = config.DEFAULT_CLIENT,
    jobdef: str = config.DEFAULT_JOB_DEFS,
    storage: str = config.DEFAULT_STORAGE,
) -> None:
    job_contents: str

    with open("templates/job.txt", "r") as f:
        job_contents = f.read()

    job_contents = job_contents.format(
        name=name, client=client, jobdef=jobdef, fileset=fileset, storage=storage
    )

    if os.path.exists(f"{config.JOB_FILE_LOCATION}/{name}.conf"):
        err_msg = (
            f"Job file for '{name}' already exists at "
            f"{config.JOB_FILE_LOCATION}/{name}.conf"
        )
        LOGGER.error(err_msg)
        raise FileExistsError(err_msg)

    with open(f"{config.JOB_FILE_LOCATION}/{name}.conf", "w") as f:
        f.write(job_contents)

    LOGGER.info(
        f"Wrote new job file at {config.JOB_FILE_LOCATION}/{name}.conf with "
        f"name={name}, fileset={fileset}, client={client}, jobdef={jobdef}, "
        f"storage={storage}"
    )


def remove_job_file(name: str) -> None:
    if os.path.exists(f"{config.JOB_FILE_LOCATION}/{name}.conf"):
        os.remove(f"{config.JOB_FILE_LOCATION}/{name}.conf")
        LOGGER.info(f"Removed job file at {config.JOB_FILE_LOCATION}/{name}.conf")
    else:
        err_msg = (
            f"Job file for '{name}' not found at {config.JOB_FILE_LOCATION}/{name}.conf"
        )
        LOGGER.error(err_msg)
        raise FileNotFoundError(err_msg)


def write_file_set_file(
    name: str, description: str, file_location: str, compression: str = "GZIP"
) -> None:
    file_contents: str

    with open("templates/fileset.txt", "r") as f:
        file_contents = f.read()

    file_contents = file_contents.format(
        name=name,
        description=description,
        file_location=file_location,
        compression=compression,
    )

    if os.path.exists(f"{config.FILESET_FILE_LOCATION}/{name}.conf"):
        err_msg = (
            f"FileSet file for '{name}' already exists at "
            f"{config.JOB_FILE_LOCATION}/{name}.conf"
        )
        LOGGER.error(err_msg)
        raise FileExistsError(err_msg)

    with open(f"{config.FILESET_FILE_LOCATION}/{name}.conf", "w") as f:
        f.write(file_contents)

    LOGGER.info(
        f"Wrote new FileSet file at {config.FILESET_FILE_LOCATION}/{name}.conf "
        f"with name={name}, description={description}, file_location={file_location}, "
        f"compression={compression}"
    )


def remove_file_set_file(name: str) -> None:
    if os.path.exists(f"{config.FILESET_FILE_LOCATION}/{name}.conf"):
        os.remove(f"{config.FILESET_FILE_LOCATION}/{name}.conf")
        LOGGER.info(
            f"Removed FileSet file at {config.FILESET_FILE_LOCATION}/{name}.conf"
        )
    else:
        err_msg = (
            f"FileSet file for '{name}' not found at "
            f"{config.JOB_FILE_LOCATION}/{name}.conf"
        )
        LOGGER.error(err_msg)
        raise FileNotFoundError(err_msg)


def reload_bconsole() -> None:
    passwd = bareos.bsock.Password(secrets.bconsole_password)

    console = bareos.bsock.DirectorConsole(
        address="localhost", port=9101, password=passwd
    )

    LOGGER.debug("Reloading Bareos Director...")
    console.call("reload")
    LOGGER.info("Reloaded Bareos director.")


def get_dir_from_db(users: List[str]) -> Dict[str, Optional[str]]:
    """Given a list of users, look up their home directory in the provided database
    in config.py.

    Returns a dictionary keyed by the provided users list with a string value of their
    home directory or 'None' when one was not found.
    """
    ret = {key: None for key in users}

    cnx = mysql.connector.connect(
        user=secrets.sql_username,
        password=secrets.sql_password,
        host=secrets.DB_HOST,
        port=secrets.DB_PORT,
        database=secrets.DB_NAME,
        connection_timeout=3,
    )

    cur = cnx.cursor()

    # The number of '%s' we need in the query statement.
    s_str = ",".join(["%s"] * len(users))
    query = f"SELECT name, homedir_source FROM accounts_user WHERE name in ({s_str})"

    cur.execute(query, tuple(users))

    for name, homedir_source in cur:
        ret[name] = homedir_source

    cur.close()
    cnx.close()

    return ret


def get_pe_dir_from_db(users: List[str]) -> List[str]:
    """Given a list of users, look up their PE home directory in the provided database
    in config.py.

    Returns a dictionary keyed by the provided users list with a string value of their
    home directory or 'None' when one was not found.
    """
    ret = {key: None for key in users}

    cnx = mysql.connector.connect(
        user=secrets.sql_username,
        password=secrets.sql_password,
        host=secrets.DB_HOST,
        port=secrets.DB_PORT,
        database=secrets.DB_NAME,
        connection_timeout=5,
    )

    cur = cnx.cursor()

    # The number of '%s' we need in the query statement.
    s_str = ",".join(["%s"] * len(users))
    query = f"SELECT name, pe_homedir_source FROM accounts_user WHERE name in ({s_str})"

    cur.execute(query, tuple(users))

    for name, homedir_source in cur:
        ret[name] = homedir_source

    cur.close()
    cnx.close()

    return ret


def push_to_gitlab(message: str) -> None:
    repo = Repo(config.GIT_LOCATION)

    if repo.bare:
        err_msg = f"{config.GIT_LOCATION} is not an initialized git repo."
        LOGGER.error(err_msg)
        raise FileNotFoundError(err_msg)

    git = repo.git
    try:
        git.pull()
        git.add(A=True)
        git.commit(m=message)
        LOGGER.info(f"Pushing to GitLab with commit message: '{message}'")
        git.push()
    except Exception as e:
        LOGGER.critical(f"Failed to push to GitLab due to: {e}")
