import click

from spell.api.runs_client import RunsClient
from spell.cli.exceptions import (
    api_client_exception_handler,
)
from spell.cli.log import logger


@click.command(name="kill",
               short_help="Kill a current run")
@click.argument("run_id")
@click.option("-q", "--quiet", is_flag=True,
              help="Suppress logging")
@click.pass_context
def kill(ctx, run_id, quiet):
    """
    Kill a current run specified by RUN_ID.

    A killed run is sent a kill signal that ends current execution and immediately
    transitions to the "Killed" state once the signal has been received. Killed
    runs do not execute any steps after being killed, so a killed run will not,
    for example, execute the "Pushing" or "Saving" steps if killed when
    in the "Running" status.
    """
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        logger.info("Killing run {}".format(run_id))
        run_client.kill_run(run_id)

    logger.info("Successfully killed run {}".format(run_id))
    if not quiet:
        click.echo(run_id)
