# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime
import click
import json
import posixpath

import requests

from api_client import exceptions, models
from spell_cli.version import __version__ as CLI_VERSION


TIME_FORMATS = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
UPDATE_MESSAGE = ("Your Spell CLI version {} is below the minimum recommended version of {}. "
                  "Please upgrade by running: \"pip install -U spell\"")

SPELL_OBJ_HOOKS = {
    "user": models.User,
    "key": models.Key,
    "keys": [models.Key],
    "workspace": models.Workspace,
    "workspaces": [models.Workspace],
    "ls": [models.LsLine],
    "template": models.Template,
    "run": models.Run,
    "runs": [models.Run],
    "cpu_stats": models.CPUStats,
    "gpu_stats": [models.GPUStats],
    "user_dataset": models.UserDataset,
    "billing_status": models.BillingStatus,
}


class SpellDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(SpellDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for k, v in obj.items():
            if k in SPELL_OBJ_HOOKS:
                spell_type = SPELL_OBJ_HOOKS[k]
                # Handle list-type objects
                if type(spell_type) == list:
                    spell_type = spell_type[0]
                    try:
                        obj[k] = [spell_type(**spell_blob) for spell_blob in v]
                    except TypeError as e:
                        raise ValueError("{} ({})".format(e, obj))
                # Handle solo objects
                else:
                    try:
                        obj[k] = spell_type(**v)
                    except TypeError as e:
                        raise ValueError("{} ({})".format(e, obj))
            else:
                # Try date objects
                for time_format in TIME_FORMATS:
                    try:
                        obj[k] = datetime.strptime(v, time_format)
                        break
                    except (ValueError, TypeError):
                        pass

        # We did it!
        return obj


class JwtAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer {}".format(self.token)
        return r


def _init_print_update_request():
    printed_update_message = [False]

    def inner(version):
        if not printed_update_message[0]:
            click.echo(click.wrap_text(UPDATE_MESSAGE.format(CLI_VERSION, version), initial_indent="✨ ",
                                       subsequent_indent="✨ "), err=True)
            printed_update_message[0] = True
    return inner


print_update_request = _init_print_update_request()


class BaseClient(object):

    def __init__(self, base_url, version_str):
        self.base_url = base_url
        self.version_str = version_str

    def request(self, method, resource_url, payload=None, token=None, stream=False):
        kwargs = {}
        kwargs["method"] = method
        kwargs["stream"] = stream
        kwargs["headers"] = {
            "User-Agent": "SpellCLI/{}".format(CLI_VERSION),
            "Accept-Encoding": "gzip",
        }
        kwargs["url"] = posixpath.join(self.base_url, self.version_str, resource_url)
        if payload:
            kwargs["data"] = json.dumps(payload)
            kwargs["headers"].update({"Content-Type": "application/json"})
        if token:
            kwargs["auth"] = JwtAuth(token)

        try:
            resp = requests.request(**kwargs)
        except requests.ConnectionError as e:
            raise exceptions.ClientException(msg="Can't reach Spell. Please check your internet connection.")
        except requests.RequestException as e:
            raise exceptions.ClientException(msg=str(e), exception=e)
        return resp

    def check_and_raise(self, response):
        cli_update_version = response.headers.get("Spell-CLI-Update")
        if cli_update_version is not None:
            print_update_request(cli_update_version)

        if response.status_code in (200, 201, 204):
            return
        error = exceptions.decode_error(response)
        if response.status_code == 401:
            raise exceptions.UnauthorizedRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 400:
            raise exceptions.BadRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 409:
            raise exceptions.ConflictRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 500:
            raise exceptions.ServerError(msg=str(error) if error else None, response=response)
        else:
            raise exceptions.ClientException(msg=str(error) if error else None, response=response)

    def get_json(self, response):
        try:
            return json.loads(response.text, cls=SpellDecoder)
        except ValueError as e:
            message = "Error decoding the response: {}".format(e)
            raise exceptions.JsonDecodeError(msg=message, response=response, exception=e)
