import yaml

from api_client import base_client
from spell_cli.utils import url_path_join


CONFIG_RESOURCE_URL = "supported_options"


class SupportedOptionsClient(base_client.BaseClient):
    def __init__(self, cache_path, base_url, version_str,
                 resource_url=CONFIG_RESOURCE_URL):
        self.cache_path = cache_path
        self.resource_url = resource_url
        super(SupportedOptionsClient, self).__init__(base_url, version_str)

    def get_options(self, config_type):
        """Get the CLI config options.

        Returns:
        a list of config options, default first (if applicable)
        """
        r = self.request("get", url_path_join(self.resource_url, config_type))
        self.check_and_raise(r)
        resp = self.get_json(r)

        opts = resp["options"]
        try:
            with open(self.cache_path) as cache_file:
                cache = yaml.safe_load(cache_file)
        except IOError:
            cache = {}
        with open(self.cache_path, 'w') as cache_file:
            cache[config_type] = {
                "values": opts['values'],
                "default": opts.get('default'),
            }
            yaml.safe_dump(cache, cache_file, default_flow_style=False)
        return opts
