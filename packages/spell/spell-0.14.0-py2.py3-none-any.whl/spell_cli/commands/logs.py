# -*- coding: utf-8 -*-
from backports.shutil_get_terminal_size import get_terminal_size
import click
import dateutil.parser
from halo import Halo
import sys
import time

from api_client.runs_client import RunsClient
from spell_cli.exceptions import (
    ExitException,
    api_client_exception_handler,
)
from spell_cli.log import logger


@click.command(name="logs",
               short_help="Retrieve logs for a run")
@click.argument("run_id")
@click.option("-d", "--delay", is_flag=True,
              help="Replay delay between log entries")
@click.option("-f", "--follow", is_flag=True,
              help="Follow log output")
@click.option("-n", "--tail", default=0,
              help="Show the last NUM lines")
@click.option("-v", "--verbose", is_flag=True,
              help="Print additional information")
@click.pass_context
def logs(ctx, run_id, delay, follow, tail, verbose, stop_status=None):
    """
    Retrieve logs for a run specified by RUN_ID.

    Streams logs for the specified run. For runs with a large number of log lines
    the `--tail N` option allows the user to print only the last N lines. When
    following with `--follow` use `Ctrl + C` to detach.
    """
    # grab the logs from the API
    token = ctx.obj["config_handler"].config.token
    run_client = RunsClient(token=token, **ctx.obj["client_args"])
    with api_client_exception_handler():
        logger.info("Retrieving run logs from Spell")
        try:
            logPrinter = LogPrinter(delay, verbose or not sys.stdout.isatty())
            for entry in run_client.get_run_log_entries(run_id, follow=follow, offset=-tail):
                logPrinter.process_entry(entry)
                if entry.get("status_event"):
                    status = entry.get("status", "")
                    if stop_status is not None and status == stop_status:
                        break
            if stop_status is not None and status != stop_status:
                raise ExitException("Run ended before entering the {} state".format(stop_status))
        except KeyboardInterrupt:
            if stop_status is not None:
                raise click.Abort()
            click.echo()
            click.echo(u"✨ Use 'spell logs {}' to view logs again".format(run_id))


class LogPrinter(object):

    default_emoji = u"✨"

    star_spinner = {
        "interval": 200,
        "frames": [u"⭐", u"🌟"],
    }

    status_emoji = {
        "running":  u"✨",
        "complete": u"🎉",
        "failed":   u"💥",
        "killing":  u"💫",
        "killed":   u"💀",
        "stopping": u"💫",
        "stopped":  u"✋",
    }

    def __init__(self, delay=False, verbose=False):
        self.delay = delay
        self.prev_datetime = None

        self.verbose = verbose

        self.spinner = None
        self.spinner_status = None

    def echo(self, *args, **kwargs):
        """Pause the active spinner and pass arguments to click.echo."""
        self.spinner and self.spinner.stop()
        click.echo(*args, **kwargs)
        self.spinner and self.spinner.start()

    def process_entry(self, entry):
        self.simulate_delay(entry.get("@timestamp"))

        status = entry.get("status")
        if entry.get("status_event"):
            self.process_status_change(status)

        message = entry.get("log")
        if self.spinner and status != "running":
            self.set_spinner_message(message)
        else:
            self.echo(message)

    def process_status_change(self, status):
        self.end_spinner()
        custom_emoji = self.status_emoji.get(status)
        if custom_emoji or self.verbose:
            self.echo((custom_emoji or self.default_emoji) + " ", nl=False)
        else:
            self.begin_spinner(status)

    def begin_spinner(self, status):
        """Create and start a new spinner."""
        self.spinner_status = status.title() + u"…"
        self.spinner = Halo(spinner=self.star_spinner)
        self.spinner.start(self.spinner_status)

    def end_spinner(self):
        """Stop and release the current spinner."""
        if not self.spinner:
            return
        self.set_spinner_message("done")
        self.spinner.stop_and_persist({"symbol": self.default_emoji})
        self.spinner = None

    def set_spinner_message(self, message):
        text = self.spinner_status
        if message:
            text += " " + message

        # truncate text to terminal width
        cols = get_terminal_size().columns
        cols -= 3  # subtract spinner columns
        if len(text) > cols:
            text = text[:cols-1] + u"…"

        self.spinner.text = text

    def simulate_delay(self, timestamp):
        try:
            dt = dateutil.parser.parse(timestamp)
        except (TypeError, ValueError) as e:
            logger.warn(e)
            return
        if self.delay and self.prev_datetime:
            delta = (dt - self.prev_datetime).total_seconds()
            if delta > 0:
                time.sleep(delta)
        self.prev_datetime = dt
