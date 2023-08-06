import requests
from blockex.tradeapi import interface

try:
    import ujson as json
    requests.models.json = json
except ImportError:
    pass


class ApiClient(object):
    """Api Client class"""

    def __init__(self, api_url=None, api_id=None):
        self.api_url = api_url if api_url else interface.DEFAULT_API_URL
        self.api_id = api_id if api_id else interface.DEFAULT_API_URL

    def get_path(self, url_path, *args, **kwargs): # pylint: disable=missing-docstring
        return requests.get(self.api_url + url_path, *args, **kwargs)

    def put_path(self, url_path, *args, **kwargs): # pylint: disable=missing-docstring
        return requests.put(self.api_url + url_path, *args, **kwargs)

    def post_path(self, url_path, *args, **kwargs): # pylint: disable=missing-docstring
        return requests.post(self.api_url + url_path, *args, **kwargs)

    def delete_path(self, url_path, *args, **kwargs): # pylint: disable=missing-docstring
        return requests.delete(self.api_url + url_path, *args, **kwargs)
