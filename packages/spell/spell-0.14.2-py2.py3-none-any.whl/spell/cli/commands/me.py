import click

from spell.api.user_client import UserClient
from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils import HiddenOption, prettify_time, tabulate_rows


# display order of columns
COLUMNS = [
    "user_name",
    "email",
    "created_at",
    "last_logged_in",
]

# title lookup
TITLES = {
    "created_at": "CREATED",
    "email": "EMAIL",
    "user_name": "USER NAME",
    "last_logged_in": "LAST LOG IN",
}


@click.command(name="whoami",
               short_help="Display current user information")
@click.option("--raw", help="Display output in raw format.", is_flag=True, default=False, cls=HiddenOption)
@click.pass_context
def me(ctx, raw):
    """
    Display current user information.

    Display information about the currently logged in user, such as username, email, and various other metadata.
    """
    client = UserClient(token=ctx.obj["config_handler"].config.token, **ctx.obj["client_args"])

    with api_client_exception_handler():
        user = client.get_user_info()

    if raw:
        click.echo("\n".join(["{},{}".format(x, y) for x, y in [val for val in user.__dict__.items()]]))
    else:
        user.last_logged_in = prettify_time(user.last_logged_in)
        user.created_at = prettify_time(user.created_at)
        tabulate_rows([user], headers=[TITLES[col] for col in COLUMNS], columns=COLUMNS)
