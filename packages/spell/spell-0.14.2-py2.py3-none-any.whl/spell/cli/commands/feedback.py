import click

from spell.api.feedback_client import FeedbackClient
from spell.cli.exceptions import (
    api_client_exception_handler,
)
from spell.cli.log import logger


@click.command(name="feedback",
               short_help="Provide feedback to the Spell team")
@click.argument("message", nargs=-1)
@click.pass_context
def feedback(ctx, message):
    """
    Submit feedback to the Spell team to identify bugs and improve Spell's products.

    We at Spell would love to hear from you! Both positive and negative feedback is
    appreciated. If reporting a bug, please provide as much detail as possible
    such as git repo, framework, runid, and any steps to reproduce. If reporting a
    feature request, we'll let you know as soon as it's been added.
    """
    config = ctx.obj["config_handler"].config
    feedback_client = FeedbackClient(token=config.token, **ctx.obj["client_args"])

    if len(message) > 0:
        message = ' '.join(message)
    else:
        message = click.edit(text="Type your message here. " +
                                  "Save and exit to send, or just exit to abort.",
                             require_save=True)
    if not message:
        click.echo("Aborted.")
    else:
        click.echo("Posting feedback to the Spell team...")
        with api_client_exception_handler():
            logger.info("Sending feedback")
            feedback_client.post_feedback(message)
        click.echo("Post complete. Thanks so much for your feedback. We'll look into it right away!")
