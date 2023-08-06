import json

from spell.api import models


class ClientException(Exception):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A client exception occurred.\n"
            url = getattr(response, "url", None)
            status_code = getattr(response, "status_code", None)
            text = getattr(response, "text", None)
            if url:
                msg += "URL: {}\n".format(url)
            if status_code:
                msg += "Response Status Code: {}\n".format(status_code)
            if text:
                msg += "Response: {}\n".format(text)
            msg = msg.rstrip()
        super(ClientException, self).__init__(msg)
        self.message = msg
        self.response = response
        self.exception = exception


class ServerError(ClientException):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A server error occured.\n"
        super(ServerError, self).__init__(msg, response, exception)


class BadRequest(ClientException):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A bad request was made.\n"
        super(BadRequest, self).__init__(msg, response, exception)


class UnauthorizedRequest(ClientException):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "An unauthorized request was made.\n"
        super(UnauthorizedRequest, self).__init__(msg, response, exception)


class ConflictRequest(ClientException):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A conflicting request was made.\n"
        super(ConflictRequest, self).__init__(msg, response, exception)


class JsonDecodeError(ClientException):

    def __init__(self, msg=None, response=None, exception=None):
        if msg is None:
            msg = "A JSON decoding error occured.\n"
        super(JsonDecodeError, self).__init__(msg, response, exception)


def decode_error(response):
    try:
        return json.loads(response.text, object_hook=models.Error.response_dict_to_object)
    except Exception:
        return None
