# -*- coding: utf-8 -*-
from six.moves.urllib.parse import quote_plus


def url_path_join(*tokens):
    return '/'.join(quote_plus(s.strip('/')) for s in tokens)
