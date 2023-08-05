import json
from six.moves import urllib

from requests.exceptions import ChunkedEncodingError

from api_client import base_client
from api_client.exceptions import ClientException, JsonDecodeError
from spell_cli.utils import url_path_join


RUNS_RESOURCE_URL = "runs"

LOGS_RESOURCE_URL = "logs"
LS_RESOURCE_URL = "ls"
KILL_RESOURCE_URL = "kill"
STOP_RESOURCE_URL = "stop"
COPY_RESOURCE_URL = "cp"
STATS_RESOURCE_URL = "stats"


class RunsClient(base_client.BaseClient):
    def __init__(self, token, base_url, version_str,
                 resource_url=RUNS_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(RunsClient, self).__init__(base_url, version_str)

    def run(self, machine_type, command='', workspace_id=0, commit_hash='', cwd='',
            pip_packages=None, apt_packages=None, docker_image=None, framework=None,
            framework_version=None, python2=None, attached_resources=None,
            envvars=None, conda_file=None, conda_name=None, run_type="user"):
        """Execute a new run.

        Keyword arguments:
        machine_type -- which machine_type to use for the actual run
        command -- the command to run on this workspaces
        workspace_id -- the id of the workspace for this repo
        commit_hash -- the current commit hash on the repo to run
        cwd -- the current working directory that the user ran this cmd in
        pip_packages -- list of pip dependencies to install
        apt_packages -- list of apt dependencies to install
        docker_image -- name of docker image to use as base
        framework -- Spell framework to use for the run, must be specified if docker_image not given
        framework_version -- Version of Spell framework to use for the run
        python2 -- a boolean indicating whether python version should be set to python 2
        attached_resources -- ids and mount points of runs to attach
        envvars -- environment variables to set
        conda_file -- contents of conda environment.yml
        conda_name -- name of conda environment to activate in run
        run_type -- type of run

        Returns:
        a Run object
        """
        payload = {
            "command": command,
            "workspace_id": workspace_id,
            "gpu": machine_type,
            "pip_packages": pip_packages if pip_packages is not None else [],
            "apt_packages": apt_packages if apt_packages is not None else [],
            "docker_image": docker_image,
            "framework": framework,
            "framework_version": framework_version,
            "python2": python2,
            "git_commit_hash": commit_hash,
            "environment_vars": envvars,
            "attached_resources": attached_resources,
            "conda_file": conda_file,
            "conda_name": conda_name,
            "run_type": run_type,
            "cwd": cwd,
        }
        r = self.request("post", self.resource_url,
                         payload=payload, token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["run"]

    def list_runs(self, workspace_id=None):
        """Get a list of runs.

        Keyword arguments:
        workspace_id -- the id of the workspace to filter the runs by [OPTIONAL]

        Returns:
        a list of Run objects for this user

        """
        url = self.resource_url
        if workspace_id is not None:
            url += "?" + urllib.parse.urlencode({'workspace_id': workspace_id})
        r = self.request("get", url, token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["runs"]

    def get_run(self, run_id):
        """Get a run.

        Keyword arguments:
        run_id -- the id of the run

        Returns:
        a Run object
        """
        r = self.request("get", url_path_join(self.resource_url, run_id), token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["run"]

    def get_run_log_entries(self, run_id, follow, offset):
        """Get log entries for a run.

        Keyword arguments:
        run_id -- the id of the run
        follow -- true if the logs should be followed
        offset -- which log line to start from

        Returns:
        a generator for entries of run logs
        """
        finished = False
        while not finished:
            if offset is None:
                raise ClientException("Missing log stream offset")
            payload = {"follow": follow, "offset": offset}
            with self.request("post", url_path_join(self.resource_url, run_id, LOGS_RESOURCE_URL),
                              payload=payload, token=self.token, stream=True) as log_stream:
                self.check_and_raise(log_stream)
                try:
                    if log_stream.encoding is None:
                        log_stream.encoding = 'utf-8'
                    for chunk in log_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk)
                        except ValueError as e:
                            message = "Error decoding the log response chunk: {}".format(e)
                            raise JsonDecodeError(msg=message, response=log_stream, exception=e)
                        offset = chunk.get("next_offset", offset)
                        logEntry = chunk.get("log_entry")
                        finished = chunk.get("finished")
                        if logEntry:
                            yield logEntry
                        elif finished:
                            break
                except ChunkedEncodingError:
                    continue  # Try reconnecting

    def remove_run(self, run_id):
        """Soft delete a run, don't show in ps or ls.

        Keyword arguments:
        run_id -- the id of the run to remove

        Returns:
        nothing if successful
        """
        r = self.request("delete", url_path_join(self.resource_url, str(run_id)),
                         token=self.token)
        self.check_and_raise(r)

    def kill_run(self, run_id):
        """Kill a currently running run.

        Keyword arguments:
        run_id -- the id of the run
        """
        r = self.request("post", url_path_join(self.resource_url, run_id, KILL_RESOURCE_URL), token=self.token)
        self.check_and_raise(r)

    def stop_run(self, run_id):
        """Stop a currently running run.

        Keyword arguments:
        run_id -- the id of the run to stop
        """
        r = self.request("post", url_path_join(self.resource_url, run_id, STOP_RESOURCE_URL), token=self.token)
        self.check_and_raise(r)

    def get_stats(self, run_id, follow=False):
        """Get statistics for a run.

        Keyword arguments:
        run_id -- the id of the run

        Returns:
        a generator of (cpu_stats, gpu_stats) tuples for the run
        """
        finished = False
        while not finished:
            payload = {"follow": follow}
            with self.request("post", url_path_join(self.resource_url, run_id, STATS_RESOURCE_URL),
                              payload=payload, token=self.token, stream=True) as stats_stream:
                self.check_and_raise(stats_stream)
                try:
                    if stats_stream.encoding is None:
                        stats_stream.encoding = 'utf-8'
                    for chunk in stats_stream.iter_lines(decode_unicode=True):
                        try:
                            chunk = json.loads(chunk, cls=base_client.SpellDecoder)
                        except ValueError as e:
                            message = "Error decoding the stats response chunk: {}".format(e)
                            raise JsonDecodeError(msg=message, response=stats_stream, exception=e)
                        cpu_stats, gpu_stats = chunk.get("cpu_stats"), chunk.get("gpu_stats")
                        finished = chunk.get("finished")
                        if cpu_stats:
                            yield (cpu_stats, gpu_stats)
                        elif finished:
                            break
                except ChunkedEncodingError:
                    continue  # Try reconnecting
