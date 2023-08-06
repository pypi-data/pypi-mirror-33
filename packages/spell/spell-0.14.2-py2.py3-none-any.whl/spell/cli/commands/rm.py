import sys

import click

from spell.api.runs_client import RunsClient
from spell.api.user_datasets_client import UserDatasetsClient
from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.log import logger


@click.command(name="rm",
               short_help="Specify one or more resources to delete. These can be [run_id] or uploads/[directory]")
@click.argument("resources", required=True, nargs=-1)
@click.pass_context
def rm(ctx, resources):
    """
    Remove one or more resources.
    To remove a finished or failed run simply use its RUN_ID.
    To remove a resource use uploads/DIRECTORY.

    The removed runs will no longer show up in `ps`. The outputs of removed runs
    and removed uploads will no longer appear in `ls` or be mountable on
    another run with `--mount`.
    """
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])
    dataset_client = UserDatasetsClient(token=token, **ctx.obj["client_args"])

    logger.info("Deleting resource={}".format(resources))
    exit_code = 0
    for resource in resources:
        try:
            with api_client_exception_handler():
                if resource.startswith("uploads/"):
                    dataset_client.remove_dataset(resource[8:])
                elif resource.startswith("runs/"):
                    run_client.remove_run(resource[5:])
                else:
                    run_client.remove_run(resource)
        except ExitException as e:
            exit_code = 1
            e.show()
    sys.exit(exit_code)
