from api_client import base_client


TEMPLATE_RESOURCE_URL = "dockertemplate"


class TemplateClient(base_client.BaseClient):
    def __init__(self, base_url, version_str,
                 token=None, resource_url=TEMPLATE_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(TemplateClient, self).__init__(base_url, version_str)

    def get_template(self):
        """Get dockerfile template

        Returns:
        the template string retrieved from the server
        """
        r = self.request("get", self.resource_url, token=self.token)
        self.check_and_raise(r)
        template = self.get_json(r)["template"]
        return template.body
