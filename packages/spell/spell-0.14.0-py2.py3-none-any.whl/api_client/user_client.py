from api_client import base_client


USER_RESOURCE_URL = "users"


class UserClient(base_client.BaseClient):
    def __init__(self, base_url, version_str,
                 token=None, resource_url=USER_RESOURCE_URL):
        self.token = token
        self.resource_url = resource_url
        super(UserClient, self).__init__(base_url, version_str)

    def create(self, user_name, email, password, full_name=None,
               organization=None, admin_override=None):
        """Create a new user at the server

        Keyword arguments:
        user_name -- user_name of the new user (must be at least 4 characters)
        email -- email of the new user
        password -- password of the new user (must be at least 8 characters)
        full_name -- optional, full name of new user
        organization -- optional, company or group new user is associated with

        Returns:
        a User object for the new user

        """
        payload = {
            "user": {
                "user_name": user_name, "password": password, "email": email,
                "full_name": full_name,
                "organization": organization},
            "admin_override": admin_override}
        r = self.request("post", self.resource_url, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["user"]

    def _login(self, user_name, email, password):
        """Log in a user to the server

        Keyword arguments:
        user_name -- user_name of the user
        email -- email of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        payload = {"user": {"user_name": user_name, "password": password,
                   "email": email}}
        r = self.request("post", "{}/{}".format(self.resource_url, "login"),
                         payload=payload)
        self.check_and_raise(r)
        self.token = self.get_json(r)["token"]
        return self.token

    def login_with_email(self, email, password):
        """Log in a user by email to the server

        Keyword arguments:
        email -- email of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login("", email, password)

    def login_with_username(self, user_name, password):
        """Log in a user by user_name to the server

        Keyword arguments:
        user_name -- user_name of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login(user_name, "", password)

    def logout(self, token=None):
        """Log out a user from the server

        Keyword arguments:
        token -- an authentication token for the user

        """
        r = self.request("post", "{}/{}".format(self.resource_url, "logout"),
                         token=(token if token else self.token))
        self.check_and_raise(r)

    def check_password(self, password):
        """Checks password for a logged-in user

        Keyword arguments:
        password -- password of the user

        Returns:
        nothing if successful
        """
        payload = {"password": password}
        r = self.request("post", "{}/{}".format(self.resource_url, "me/check_password"),
                         token=self.token, payload=payload)
        self.check_and_raise(r)

    def change_password(self, old_password, new_password):
        """Change password for a logged-in user, require password before changing

        Keyword arguments:
        old_password -- current password for the user
        new_password -- new password for the user

        Returns:
        nothing if successful

        """
        payload = {
            "new_password": new_password,
            "old_password": old_password,
        }
        r = self.request("put", "{}/{}".format(self.resource_url, "me/change_password"),
                         token=self.token, payload=payload)
        self.check_and_raise(r)

    def get_user_info(self, token=None):
        """Get user information from the server

        Keyword arguments:
        token -- an authentication token for the user

        Returns:
        a User object for the user

        """
        r = self.request("get", "{}/{}".format(self.resource_url, "me"),
                         token=(token if token else self.token))
        self.check_and_raise(r)
        return self.get_json(r)["user"]

    def get_billing_info(self, token=None):
        """Get user billing information from the server

        Keyword arguments:
        token -- an authentication token for the user

        Returns:
        a Billing object for the user

        """
        r = self.request("get", "{}/{}".format(self.resource_url, "me/status"),
                         token=(token if token else self.token))
        self.check_and_raise(r)
        return self.get_json(r)["billing_status"]
