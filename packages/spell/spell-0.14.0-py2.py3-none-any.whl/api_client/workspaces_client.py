from api_client import base_client
from six.moves import urllib


WORKSPACES_RESOURCE_URL = "workspaces"


class WorkspacesClient(base_client.BaseClient):
    def __init__(self, token, base_url, version_str,
                 resource_url=WORKSPACES_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(WorkspacesClient, self).__init__(base_url, version_str)

    def new_workspace(self, root_commit, name, description):
        """Create a new workspace.

        Keyword arguments:
        name -- the name of the workspace
        description -- the description of the workspace

        Returns:
        a Workspace object for the created workspace

        """
        payload = {
            "root_commit": root_commit,
            "name": name,
            "description": description,
        }
        r = self.request("put", self.resource_url,
                         payload=payload, token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["workspace"]

    def get_workspaces(self):
        """Get a list of workspaces.

        Returns:
        a list of Workspace objects for this user

        """
        r = self.request("get", self.resource_url, token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["workspaces"]

    def get_workspace_by_name(self, name):
        """Get a list of workspaces.

        Keyword arguments:
        name -- the name of the workspace

        Returns:
        a list of Workspace objects for this user

        """
        r = self.request("get", self.resource_url + "?" + urllib.parse.urlencode({'name': name}),
                         token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["workspaces"][0]

    def get_workspace(self, ws_id):
        """Get a workspace.

        Keyword arguments:
        ws_id -- the id of the workspace

        Returns:
        a Workspace object
        """
        r = self.request("get", "{}/{}".format(self.resource_url, ws_id), token=self.token)
        self.check_and_raise(r)
        return self.get_json(r)["workspace"]

    def delete_workspace(self, ws_id):
        """Delete a workspace.

        Keyword arguments:
        ws_id -- the id of the workspace
        """
        r = self.request("delete", "{}/{}".format(self.resource_url, ws_id), token=self.token)
        self.check_and_raise(r)
