import json
import os
import sys
import tarfile
import tempfile

from api_client import base_client, models
from api_client.exceptions import JsonDecodeError
from spell_cli.utils import prettify_size, url_path_join

RESOURCES_RESOURCE_URL = "resources"
LS_RESOURCE_URL = "ls"
COPY_RESOURCE_URL = "cp"
CP_CHUNK_SIZE = 1024


class ResourcesClient(base_client.BaseClient):
    def __init__(self, token, base_url, version_str,
                 resource_url=RESOURCES_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(ResourcesClient, self).__init__(base_url, version_str)

    def get_ls(self, path):
        """Get file list from Spell.

        Keyword arguments:
        path -- the path to list the contents of

        Returns:
        a generator for file details
        """

        endpoint = url_path_join(self.resource_url, LS_RESOURCE_URL, *path.split('/'))
        with self.request("get", endpoint, token=self.token, stream=True) as ls_stream:
            self.check_and_raise(ls_stream)
            if ls_stream.encoding is None:
                ls_stream.encoding = 'utf-8'
            for chunk in ls_stream.iter_lines(decode_unicode=True):
                try:
                    chunk = json.loads(chunk, cls=LsLineDecoder)
                except ValueError as e:
                    message = "Error decoding the ls response chunk: {}".format(e)
                    raise JsonDecodeError(msg=message, response=ls_stream, exception=e)
                yield chunk

    def copy_file(self, local_dir, source_path):
        """Copy new files from a finished run.

        Keyword arguments:
        local_dir -- the directory to extract to
        source_path -- a single file or directory to extract, relative path (probably starting with runs/)
        """
        endpoint = url_path_join(self.resource_url, COPY_RESOURCE_URL, *source_path.split('/'))
        r = self.request("get", endpoint, token=self.token, stream=True)
        self.check_and_raise(r)
        is_directory = "Is-Directory" in r.headers

        head, tail = os.path.split(source_path)
        localfile = os.path.join(local_dir, tail)
        dirname = os.path.dirname(localfile)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        count = 0
        with (tempfile.TemporaryFile() if is_directory else open(localfile, 'wb')) as f:
            if is_directory:
                print("Downloading")
            else:
                print("Copying file to {}".format(localfile))
            for chunk in r.iter_content(chunk_size=CP_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

                    # Show a spinner and display current total size of download
                    count += 1
                    if count % 100 == 0:
                        size = prettify_size(count * CP_CHUNK_SIZE)
                        spinner = ['-', '\\', '|', '/'][int(count / 100) % 4]
                        sys.stdout.write('{} {}        \r'.format(spinner, size))
                        sys.stdout.flush()

            # Extract all files from tar
            if is_directory:
                f.seek(0)
                tar = tarfile.open(fileobj=f)
                for member in tar.getmembers():
                    if member.isdev():
                        # isdev() means it's one of character device, block device or FIFO
                        continue
                    tar.extract(member.name, path=local_dir)
                    print("Copying file to {}".format(
                        os.path.abspath(os.path.join(local_dir, member.name))))

        sys.stdout.write('{}       \n'.format(prettify_size(count * CP_CHUNK_SIZE)))
        sys.stdout.flush()
        return localfile


class LsLineDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(LsLineDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        try:
            return models.LsLine(**obj)
        except TypeError:
            return models.Error.response_dict_to_object(obj)
