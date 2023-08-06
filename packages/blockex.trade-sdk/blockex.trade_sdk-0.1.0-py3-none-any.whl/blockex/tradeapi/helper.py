import requests


class DictConditional(dict):
    """Make conditional dict by default 'DictNotNone'
       dcond = DictConditional(cond=lambda x: x != 0)
       dcond["foo"] = 0   # should not create key
       assert "foo" not in dcond
    """

    def __init__(self, __cond__=lambda x: x is not None, *args, **kwargs):
        self.__cond__ = __cond__
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if key in self or self.__cond__(value):
            dict.__setitem__(self, key, value)


def head(your_list, default=None):
    """Simple head function implementation."""
    return next(iter(your_list or []), default)


def message_raiser(base_str, *args, **kwargs):
    """Simple raiser function. For formating and raise requests.RequestException"""
    exception_message = base_str.format(*args, **kwargs)
    raise requests.RequestException(exception_message)


def get_error_message(response):
    """Gets an error message for a response."""
    response_json = response.json()
    message = response_json.get('error') or response_json.get('message')
    message = message if message else ''
    return ' Message: {message}'.format(message=message)
