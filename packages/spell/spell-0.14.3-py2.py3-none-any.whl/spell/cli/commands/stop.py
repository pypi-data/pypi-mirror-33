import click

from spell.api.runs_client import RunsClient
from spell.cli.exceptions import (
    api_client_exception_handler,
)
from spell.cli.log import logger


@click.command(name="stop",
               short_help="Stop a run with status 'Running'")
@click.argument("run_id")
@click.option("-q", "--quiet", is_flag=True,
              help="Suppress logging")
@click.pass_context
def stop(ctx, run_id, quiet):
    """
    Stop a run currently in the 'Running' state specified by RUN_ID.

    A stopped run is sent a stop signal that ends current execution and
    transitions to the "Saving" state once the signal has been received. Stopped
    runs will execute any and all steps after being stopped, so a stopped run will,
    for example, execute both the "Pushing" and "Saving" steps after stopping.
    """
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        logger.info("Stopping run {}".format(run_id))
        run_client.stop_run(run_id)

    if not quiet:
        click.echo("Stopping run {}. Use 'spell logs -f {}' to view logs while job saves".format(run_id, run_id))
