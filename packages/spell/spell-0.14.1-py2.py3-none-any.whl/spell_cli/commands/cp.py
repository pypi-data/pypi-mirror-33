import click

from api_client.resources_client import ResourcesClient
from spell_cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell_cli.log import logger


@click.command(name="cp",
               short_help="Retrieve a file or directory")
@click.argument("source_path")
@click.argument("local_dir", type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True), default=".")
@click.pass_context
def cp(ctx, source_path, local_dir):
    """
    Copy a file or directory from a finished run, uploaded resource, or public dataset
    specified by SOURCE_PATH to a LOCAL_DIR.

    The contents of SOURCE_PATH will be downloaded from Spell and written to LOCAL_DIR.
    If LOCAL_DIR is not provided the current working directory will be used as a default.
    If SOURCE_PATH is a directory, the contents of the directory will be written to LOCAL_DIR.
    """
    token = ctx.obj["config_handler"].config.token
    resources_client = ResourcesClient(token=token, **ctx.obj["client_args"])

    if source_path.startswith('/'):
        msg = 'Invalid source specification "{}". Source path must be a relative path.'.format(source_path)
        raise ExitException(msg, SPELL_INVALID_CONFIG)

    with api_client_exception_handler():
        logger.info("Copying run files from Spell")
        resources_client.copy_file(local_dir=local_dir, source_path=source_path)
