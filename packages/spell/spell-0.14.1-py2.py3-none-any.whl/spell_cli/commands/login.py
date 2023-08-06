import click
import os
import re

from spell_cli.commands.keys import cli_key_path, generate, get_remote_key
from spell_cli.commands.logout import logout
from spell_cli.log import logger
from api_client.user_client import UserClient
from api_client.exceptions import UnauthorizedRequest
from spell_cli.exceptions import ExitException, api_client_exception_handler


@click.command(name="login", short_help="Log in with your username or email")
@click.pass_context
@click.option("--identity", "identity",
              prompt="Enter your spell username or email",
              help="your registered spell username or email")
@click.password_option(prompt="Enter your spell password",
                       help="your registered spell password",
                       confirmation_prompt=False)
def login(ctx, identity, password):
    """
    Log in with your username or email.

    Prompts for the user's credentials and logs in to Spell. Both username and
    email are valid for login. If you don't have an account with Spell, please
    create one at https://spell.run.
    """
    config_handler = ctx.obj["config_handler"]
    config = config_handler.config

    # Log out existing session if it's for a different account
    if config:
        current_id = config.email if is_email(identity) else config.user_name
        if identity != current_id:
            try:
                ctx.invoke(logout, quiet=True)
            except Exception as e:
                logger.warning("Log out failed for previous session: %s", e)

    if config_handler.config is None:
        config_handler.load_default_config(type="global")

    config = config_handler.config
    client = UserClient(**ctx.obj["client_args"])

    with api_client_exception_handler():
        try:
            if is_email(identity):
                token = client.login_with_email(identity, password)
            else:
                token = client.login_with_username(identity, password)
        except UnauthorizedRequest as exception:
            raise ExitException(str(exception))

    config.token = token
    logger.info("Sucessfully retrieved user token.")

    with api_client_exception_handler():
        user = client.get_user_info(token)

    config.user_name = user.user_name
    config.email = user.email
    config_handler.write()

    # Generate CLI key for user if one does not exist, or if the existing one
    # is not registered with the user's Spell account
    local_key = cli_key_path(config_handler)
    matching_remote_key = os.path.isfile(local_key) and get_remote_key(ctx, local_key)
    if not matching_remote_key:
        ctx.invoke(generate, force=True)

    click.echo("Hello, {}!".format(user_addressing_noun(user)))


def is_email(input):
    return (re.match(".+@.+[.].+", input) is not None)


def user_addressing_noun(user):
    nouns = [user.full_name, user.user_name, user.email]
    return next((s for s in nouns if s), "")
