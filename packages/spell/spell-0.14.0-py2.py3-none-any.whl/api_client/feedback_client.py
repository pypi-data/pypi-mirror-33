from api_client import base_client


USER_RESOURCE_URL = "feedback"


class FeedbackClient(base_client.BaseClient):
    def __init__(self, base_url, version_str,
                 token=None, resource_url=USER_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(FeedbackClient, self).__init__(base_url, version_str)

    def post_feedback(self, content):
        """Post feedback to the team.

        Keyword arguments:
        content -- the content of the feedback to post

        Returns:
        None
        """
        payload = {
            "content": content,
        }
        r = self.request("post", self.resource_url, payload=payload, token=self.token)
        self.check_and_raise(r)
