import click

from api_client.exceptions import UnauthorizedRequest
from api_client.user_client import UserClient
from spell_cli.commands.keys import remove_cli_key


@click.command(name="logout", help="Log out of current session")
@click.pass_context
def logout(ctx, quiet=False):
    config_handler = ctx.obj["config_handler"]

    # Remove CLI's SSH key both locally and from Spell account
    try:
        remove_cli_key(ctx)
    except UnauthorizedRequest:
        pass

    # Hit logout endpoint to invalidate token
    token = config_handler.config.token
    user_client = UserClient(token=token, **ctx.obj["client_args"])
    try:
        user_client.logout()
    except UnauthorizedRequest:
        pass

    # Delete Spell config
    config_handler.remove_config_file()
    config_handler.config = None

    if not quiet:
        click.echo("Bye!")
