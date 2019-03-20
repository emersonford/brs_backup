#!/usr/bin/env python3

from typing import List
import sys

import click

import logger
from util import (
    get_dir_from_db,
    get_pe_dir_from_db,
    write_file_set_file,
    write_job_file,
    remove_file_set_file,
    remove_job_file,
    reload_bconsole,
    push_to_gitlab,
)
import config

LOGGER = logger.get_logger(__name__)


@click.group()
def cli():
    """brs_backup is a tool to add and remove user and group home directories from the
    Bareos backup system.
    """
    pass


@cli.command("uadd", short_help="Add user home directories to backups")
@click.option(
    "-p",
    is_flag=True,
    default=False,
    help="Add PE directories as opposed to their standard home directory.",
)
@click.option(
    "--compression",
    required=False,
    type=click.Choice(config.COMPRESSION_OPTIONS),
    help="The compression to use on these user's backups (ex: GZIP6).",
)
@click.argument("users", nargs=-1, type=str)
def uadd(p: bool, compression: str, users: List[str]):
    """Add a user's home directory to the backup system.

    \b
    Example:
    brs_backup uadd u0407846
    brs_backup uadd u0407846 u1234567 --compression=GZIP
    brs_backup uadd -p u0407846
    brs_backup uadd -p u0407846 u1234567
    """
    success = []
    failures = []

    if p:
        directories = get_pe_dir_from_db(users)
    else:
        directories = get_dir_from_db(users)

    print(p)
    print(directories)
    return

    for user in users:
        if user not in directories:
            failures.append(user)
            continue

        # Make the file set file.
        try:
            if compression:
                write_file_set_file(
                    user,
                    f"Home directory for {user}",
                    directories[user].split(":")[1],
                    compression,
                )
            else:
                write_file_set_file(
                    user, f"Home directory for {user}", directories[user].split(":")[1]
                )
        except BaseException as e:
            LOGGER.error(str(e))
            failures.append(user)

        # Make the job file.
        try:
            write_job_file(user, user, client=directories[user].split(":")[0])
        except BaseException as e:
            LOGGER.error(e)
            # If we couldn't make the job file, try cleaning up the fileset file.
            try:
                remove_file_set_file(user)
            except BaseException:
                LOGGER.error(
                    f"Failed FileSet file cleanup for {user} when Job file creation "
                    f"failed."
                )

            failures.append(user)

        success.append(user)

    # Only reload/push when files were changed.
    if success:
        reload_bconsole()
        push_to_gitlab(
            f"Ran command: brs_backup uadd {'-p ' if p else ''}{' '.join(users)}"
        )

    click.echo("success: " + ", ".join(success))
    click.echo("failure: " + ", ".join(failures))

    if len(failures) == 0:
        sys.exit(0)
    elif len(success) == 0:
        sys.exit(1)
    else:
        sys.exit(2)


@cli.command("uremove", short_help="Remove user home directories from backups")
@click.option(
    "-p",
    is_flag=True,
    default=False,
    help="Remove PE directories as opposed to their standard home directory.",
)
@click.argument("users", nargs=-1, type=str)
def uremove(p: bool, users: List[str]):
    """Remove a users's home directory from the backup system.

    \b
    Example:
    brs_backup uremove u0407846
    brs_backup uremove u0407846 u1234567
    brs_backup uremove -p u0407846
    brs_backup uremove -p u0407846 u1234567
    """
    success = []
    failures = []

    if p:
        directories = get_dir_from_db(users)
    else:
        directories = get_pe_dir_from_db(users)

    for user in users:
        if user not in directories:
            failures.append(user)
            continue

        # Remove the job file.
        try:
            remove_job_file(user)
        except BaseException as e:
            LOGGER.error(e)
            failures.append(user)

        # Remove the file set file.
        try:
            remove_file_set_file(user)
        except BaseException as e:
            LOGGER.error(e)
            failures.append(user)

        success.append(user)

    # Only reload/push when files were changed.
    if success:
        reload_bconsole()
        push_to_gitlab(
            f"Ran command: brs_backup uremove {'-p ' if p else ''}{' '.join(users)}"
        )

    click.echo("success: " + ", ".join(success))
    click.echo("failure: " + ", ".join(failures))

    if len(failures) == 0:
        sys.exit(0)
    elif len(success) == 0:
        sys.exit(1)
    else:
        sys.exit(2)


@cli.command("add", short_help="Add a directory to backups")
@click.argument("job_name", nargs=1, type=str)
@click.argument("directory", nargs=1, type=str)
@click.option(
    "--compression",
    required=False,
    type=click.Choice(config.COMPRESSION_OPTIONS),
    help="The compression to use on these directories (ex: GZIP6).",
)
def add(job_name: str, directory: str, compression: str):
    """Add a directory to the backup system, likely being group directories.

    \b
    Example:
    brs_backup add horel-group3 saltflats-vg3-1-lv1.chpc.utah.edu:/uufs/saltflats/common/saltflats-vg3-1-lv1/horel
    brs_backup add horel-group4 saltflats-vg6-0-lv1.chpc.utah.edu:/uufs/saltflats/common/saltflats-vg6-0-lv1/horel --compression=GZIP
    """  # noqa: E501
    # Create the FileSet file.
    try:
        if compression:
            write_file_set_file(
                job_name,
                f"Group space for {job_name}",
                directory.split(":")[1],
                compression,
            )
        else:
            write_file_set_file(
                job_name, f"Group space for {job_name}", directory.split(":")[1]
            )
    except BaseException as e:
        LOGGER.error(e)
        click.echo("failed")
        sys.exit(1)
        return

    # Create the Job file.
    try:
        write_job_file(job_name, job_name, client=directory.split(":")[0])
    except BaseException as e:
        LOGGER.error(e)
        # Try to clean up FileSet files.
        try:
            remove_file_set_file(job_name)
        except BaseException:
            LOGGER.error(
                f"Failed FileSet file cleanup for {job_name} when Job file creation "
                f"failed."
            )

        click.echo("failed")
        sys.exit(1)
        return

    reload_bconsole()
    push_to_gitlab(f"Ran command: brs_backup add {job_name} {directory}")

    click.echo("success")
    sys.exit(0)


@cli.command("remove", short_help="Remove a directory from backups")
@click.argument("job_name", nargs=1, type=str)
def gremove(job_name: str):
    """Remove a directory from the backup system with the given
    job name.

    \b
    Example:
    brs_backup remove horel-group3
    brs_backup remove horel-group4
    """
    # Delete the job file.
    try:
        remove_job_file(job_name)
    except BaseException as e:
        LOGGER.error(e)
        click.echo("failed")
        sys.exit(1)
        return

    # Delete the FileSet file.
    try:
        remove_file_set_file(job_name)
    except BaseException as e:
        LOGGER.error(e)
        click.echo("failed")
        sys.exit(1)
        return

    reload_bconsole()
    push_to_gitlab(f"Ran command: brs_backup remove {job_name}")

    click.echo("success")
    sys.exit(0)


if __name__ == "__main__":
    cli()
