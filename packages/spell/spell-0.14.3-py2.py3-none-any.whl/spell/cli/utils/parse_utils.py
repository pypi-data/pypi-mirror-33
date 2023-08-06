class ParseException(Exception):
    def __init__(self, message, token):
        super(ParseException, self).__init__(message)
        self.token = token


def parse_attached_resources(raw):
    attached_resources = {}
    for token in raw:
        chunks = token.split(':')
        if len(chunks) == 1:
            resource_name, path = token, ""
        elif len(chunks) == 2:
            resource_name, path = chunks
        else:
            raise ParseException("Invalid attached resource value", token)
        attached_resources[resource_name] = {"mount_point": path}
    return attached_resources


def parse_env_vars(raw):
    envvars = {}
    for envvar_str in raw:
        key_val_split = envvar_str.split('=')
        key = key_val_split[0]
        val = '='.join(key_val_split[1:])
        envvars[key] = val
    return envvars
