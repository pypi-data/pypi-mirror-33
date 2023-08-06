# -*- coding: utf-8 -*-
import click

from spell.api.resources_client import ResourcesClient
from spell.api import models
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import (
    prettify_size,
    convert_to_local_time,
    truncate_string,
)


# display order of columns
COLUMNS = [
    "size",
    "date",
    "path",
]


@click.command(name="ls",
               short_help="List resource files")
@click.argument("path", default="")
@click.option("-h", "human_readable", help="Display file sizes in human-readable format",
              is_flag=True, default=False)
@click.pass_context
def ls(ctx, path, human_readable):
    """
    List resource files for datasets, run outputs, and uploads.

    Resources are the generic name for datasets, models, or any other files that
    can be made available to a run. Spell keeps these organized for you in a
    remote filesystem that is browsable with the `ls` command, with the resources
    placed into directories that reflect their origin.

    There are many ways resources are generated. The user can upload resources
    directly with `spell upload` or execute a run with `spell run` that writes
    files to disk. Spell also provides a number of publicly-accessible datasets.
    """
    # grab the ls from the API
    token = ctx.obj["config_handler"].config.token
    r_client = ResourcesClient(token=token, **ctx.obj["client_args"])

    def format_ls_line(ls_line):
        if ls_line.date:
            ls_line.date = convert_to_local_time(ls_line.date, include_seconds=False)
        else:
            ls_line.date = "-"

        if ls_line.size is None:
            ls_line.size = "-"
        elif human_readable:
            ls_line.size = prettify_size(ls_line.size)

        status_suffix = ""
        if ls_line.additional_info:
            status_suffix = " ({})".format(ls_line.additional_info)

        ls_line.date = truncate_string(ls_line.date, 14, fixed_width=True)
        ls_line.size = truncate_string(ls_line.size, 8, fixed_width=True)
        ls_line.path = truncate_string(ls_line.path, 60-len(status_suffix), fixed_width=True) + status_suffix
        return " ".join([ls_line.size, ls_line.date, ls_line.path])

    found_a_line = False
    with api_client_exception_handler():
        logger.info("Retrieving resource list from Spell")
        for l in r_client.get_ls(path):
            found_a_line = True
            if isinstance(l, models.Error):
                raise ExitException(l.status)
            else:
                click.echo(format_ls_line(l))

    if not found_a_line:
        click.echo("No files for path {}".format(path), err=True)
        return
