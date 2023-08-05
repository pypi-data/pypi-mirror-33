# -*- coding: utf-8 -*-
import csv
from datetime import datetime, timedelta
from dateutil import parser, tz
import math
import os
import shutil

import click
import tabulate
from six.moves.urllib.parse import quote_plus

from spell_cli.log import logger


SIZE_SUFFIXES = ["B", "K", "M", "G", "T", "P"]


def tabulate_rows(rows, headers=None, columns=None, raw=False):
    def extract_attrs(row_objs):
        for row_obj in row_objs:
            yield [getattr(row_obj, col) for col in columns]

    if headers is None:
        headers = ()

    if columns is not None:
        rows = extract_attrs(rows)

    if raw:
        echo_raw(rows)
    else:
        click.echo(tabulate.tabulate(rows,
                                     headers=headers,
                                     tablefmt="plain",
                                     numalign="left"))


# convert_to_local_time is an alternative to prettify_time that returns the input
# timestamp string in a non-relative way, similar to the way that `ls -al` prints
# timestamps in the local timezone of the user
def convert_to_local_time(t, include_seconds=True):
    if isinstance(t, datetime):
        dt = t.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
    else:
        dt = parser.parse(t).astimezone(tz.tzlocal())
    if datetime.now(tz.tzlocal()) - dt < timedelta(days=364):
        format_str = "%b %d %H:%M:%S" if include_seconds else "%b %d %H:%M"
        return dt.strftime(format_str)
    else:
        return dt.strftime("%b %d %Y")


# prettify_time returns a nice human readable representation of a time delta
# if the default elapsed=False is specified, the return value describes a historical time (e.g., " 2 days ago")
# if elapsed=True, the return value describes an elapsed time (e.g, "2 days")
def prettify_time(time, elapsed=False):
    """prettify a datetime object"""
    post_fix = "" if elapsed else " ago"
    delta = datetime.utcnow() - time
    if delta.days > 14 and not elapsed:
        # date for differences of over 2 weeks
        return "{:%Y-%m-%d}".format(time)
    if delta.days > 1:
        # days ago for differences of over a day
        return "{} days{}".format(delta.days, post_fix)
    if delta.days > 0:
        return "1 day{}".format(post_fix)
    if delta.seconds > 7200:
        # hours ago for differences of over an hour
        return "{} hours{}".format(delta.seconds // 3600, post_fix)
    if delta.seconds > 3600:
        return "1 hour{}".format(post_fix)
    if delta.seconds > 120:
        # minutes ago for differences of over a minute
        return "{} minutes{}".format(delta.seconds // 60, post_fix)
    if delta.seconds > 60:
        return "1 minute{}".format(post_fix)
    return "{} seconds{}".format(delta.seconds, post_fix)


def prettify_size(size):
    """prettify an int representing file size in bytes"""
    if size < 0:
        raise ValueError("Negative size value {}".format(size))
    if size is 0:
        return "0B"

    order = int(math.log(size, 2) / 10)
    if order is 0:
        return "{}B".format(size)
    if order >= len(SIZE_SUFFIXES):
        raise ValueError("Unparsable size value {}".format(size))
    size_suffix = SIZE_SUFFIXES[order]

    scaled = size / 2**(10.*order)
    if scaled >= 10:
        return "{}{}".format(int(scaled), size_suffix)
    return "{:.1f}{}".format(scaled, size_suffix)


def truncate_string(raw, width, fixed_width=False):
    truncated = False

    s = str(raw)
    split = s.split('\n')
    if len(split) > 1:
        s = split[0]
        truncated = True
    if len(s) > width:
        s = s[:width-1]
        truncated = True
    if truncated:
        s = s + "…"
    if fixed_width:
        s = s.ljust(width)
    if hasattr(s, "decode"):
        # Convert to unicode object in Python 2
        s = s.decode("utf-8")
    return s


def echo_raw(data):
    """print rows of data (iterable of iterables) to stdout in CSV form"""
    ts = click.get_text_stream('stdout')
    writer = csv.writer(ts)
    for row in data:
        writer.writerow(row)


def remove_path(path, prompt=False):
    """remove file or directory at path"""
    if os.path.isdir(path):
        if prompt:
            click.confirm("Spell will now delete the existing directory {}. Do you wish to continue?".format(path),
                          abort=True)
        logger.info("removing existing directory: {}".format(path))
        shutil.rmtree(path)
    if os.path.isfile(path):
        if prompt:
            click.confirm("Spell will now delete the existing file {}. Do you wish to continue?".format(path),
                          abort=True)
        logger.info("removing existing file: {}".format(path))
        os.remove(path)


def default_spell_dir():
    return os.path.join(click.get_app_dir("spell", force_posix=True))


def url_path_join(*tokens):
    return '/'.join(quote_plus(s.strip('/')) for s in tokens)


class LazyChoice(click.Choice):
    """ A type similar to click.Choice that loads its choices lazily. It is initialized with a function that
    returns an iterable (probably a generator) for the possible choices. It can optionally be case-sensitive
    or insensitive, and it defaults to case-insensitive
    """

    name = 'lazy_choice'

    def __init__(self, choice_fn, case_sensitive=False):
        self.choice_fn = choice_fn
        self.case_sensitive = case_sensitive
        super(LazyChoice, self).__init__(self.choice_fn())

    def __getattribute__(self, name):
        # Override any calls to "choices" with the generator
        if name is "choices":
            return self.choice_fn()
        return super(LazyChoice, self).__getattribute__(name)

    def convert(self, value, param, ctx):
        if value is None:
            return None
        for choice in self.choices:
            if self.case_sensitive and value == choice or \
               not self.case_sensitive and value.lower() == choice.lower():
                return choice
        self.fail('invalid choice: {}. (choose from {})'.format(
            value, ', '.join(self.choices)), param, ctx)


class HiddenOption(click.Option):
    """ A subclass of click.Option that hides its existence from help outputs """

    def get_help_record(self, ctx):
        return
