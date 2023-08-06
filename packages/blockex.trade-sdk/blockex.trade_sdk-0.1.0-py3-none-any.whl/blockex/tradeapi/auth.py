"""BlockEx Trade API auth library"""
import datetime

from blockex.tradeapi import interface

from .apiclient import ApiClient
from .helper import get_error_message, message_raiser


class Auth(ApiClient):
    """Auth class. Takes all auxiliary functions for login processes"""

    def __init__(self, username, password, api_url, api_id):
        assert username
        assert password

        self.username = username
        self.password = password
        self.access_token = None
        self.access_token_expires = None

        ApiClient.__init__(self, api_url, api_id)

    @staticmethod
    def is_unauthorized_response(response):
        """Checks if a response is unauthorized."""
        if response.status_code == interface.UNAUTHORIZED:
            response_content = response.json()
            message = 'Authorization has been denied for this request.'
            if 'message' in response_content:
                if response_content['message'] == message:
                    return True
        return False

    def _method_caller(self, method, url):
        bearer = self.access_token if self.access_token else ''
        headers = {'Authorization': "Bearer {bearer}".format(bearer=bearer)}
        return method(url, headers=headers)

    def make_authorized_request(self, method, url):
        """Helper function for make authorized request"""
        # Not logged in or the access token has expired
        current_time = datetime.datetime.now()
        if not self.access_token or self.access_token_expires < current_time:
            self.login()

        response = self._method_caller(method, url)

        if self.is_unauthorized_response(response):
            self.login()
            response = self._method_caller(method, url)

        return response

    def get_access_token(self):
        """Gets the access token.

        :returns: The access token of the logged
        :rtype: dict
        :raises: requests.RequestException

        """

        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'client_id': self.api_id
        }

        response = self.post_path(interface.ApiPath.LOGIN.value, data=data)
        if response.status_code == interface.SUCCESS:
            return response.json()

        message_raiser('Login failed. {error_message}', error_message=get_error_message(response))

    def login(self):
        """
        Performs a login and stores the received access token.

        :returns: The access token of the logged in trader
        :rtype: dict
        :raises: requests.RequestException

        """
        access_token = self.get_access_token()
        self.access_token = access_token['access_token']
        self.access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=access_token['expires_in'])
        return self.access_token

    def logout(self):
        """
        Performs a logout when logged in and deletes the stored access token.

        :raises: requests.RequestException

        """

        if self.access_token is not None:
            headers = {'Authorization': 'Bearer ' + self.access_token}
            response = self.post_path(interface.ApiPath.LOGOUT.value, headers=headers)
            if response.status_code != interface.SUCCESS:
                message_raiser('Logout failed. {error_message}', error_message=get_error_message(response))

            self.access_token = None
