import time

from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests_oauthlib import OAuth2Session

from .credentials import Credentials

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

PINGBOARD_OAUTH_URL = 'https://app.pingboard.com/oauth'
PINGBOARD_TOKEN_URL = PINGBOARD_OAUTH_URL + '/token?grant_type=client_credentials'

PINGBOARD_API_URL = 'https://app.pingboard.com/api/v2/'
PINGBOARD_TOKEN_MAX_RETRIES = 5

class PingboardClient:

    def __init__(self, **kwargs):

        if 'client_id' in kwargs and 'client_secret' in kwargs:
            self.__credentials = Credentials(**kwargs)
        else:
            self.__credentials = kwargs.get('credentials')
            if self.__credentials is None:
                self.__credentials = Credentials()

        if not self.__credentials.load():
            raise Exception("Could not load credentials from any source")

        self.__init_oauth()

    def __init_oauth(self):
        self.__client = BackendApplicationClient(client_id=self.__credentials.client_id)
        self.__get_new_session()

    def __set_token(self, token):
        self.__token = token

    def __get_token(self, session):
        count = 0
        token = None
        # PB sometimes returns an expired token. If this is the case, retry with a back off until a valid token is given
        # or the max retries is hit.
        while count < PINGBOARD_TOKEN_MAX_RETRIES:
            token = session.fetch_token(token_url=PINGBOARD_TOKEN_URL,
                                        client_id=self.__credentials.client_id,
                                        client_secret=self.__credentials.client_secret)
            count += 1
            if token.get('expires_at') > time.time():
                break
            else:
                time.sleep(count)

        return token

    def __get_new_session(self):
        session = OAuth2Session(client=self.__client)
        self.__session = OAuth2Session(client=self.__client,
                                       token=self.__get_token(session),
                                       token_updater=self.__set_token)
        return

    def __request(self, method, url, body=None):
        try:
            return self.__session.request(method, PINGBOARD_API_URL + url, body)
        except TokenExpiredError:
            # token expired. get a new one
            self.__get_new_session()
            return self.__session.request(method, PINGBOARD_API_URL + url, body)

    def __paging_get(self, endpoint, **kwargs):
        result = None
        if 'page_size' not in kwargs:
            kwargs['page_size'] = 500
        kwargs['page'] = 1
        while True:
            response = self.__request("GET", endpoint + "?" + urlencode(kwargs, False))
            if response.status_code is not 200:
                raise Exception("Unexpected status code " + str(response.status_code))
            response = response.json()
            if result is None:
                result = response
            else:
                result[endpoint] += response[endpoint]
                result['meta'] = response['meta']
            if len(response[endpoint]) < kwargs['page_size'] or (
                'max_size' in kwargs and len(result[endpoint]) >= kwargs['max_size']):
                break
            else:
                kwargs['page'] += 1

        if 'max_size' in kwargs:
            if len(result[endpoint]) - kwargs['max_size'] > 0:
                result[endpoint] = result[endpoint][:kwargs['max_size']]

        return result[endpoint];

    def get_user(self, user_id, *includes):
        response = self.__request("GET", "users/" + str(user_id) + "?include=" + ",".join(includes))
        if response.status_code is 200:
            return response.json()['users'][0]

        return None

    def get_users(self, **kwargs):
        response = self.__request("GET", "users?" + urlencode(kwargs, False))
        if response.status_code is 200:
            return response.json()['users']

        return None

    def get_all_users(self, **kwargs):
        return self.__paging_get("users", **kwargs)

    def get_group(self, group_id, *includes):
        response = self.__request("GET", "groups/" + str(group_id) + "?include=" + ",".join(includes))
        if response.status_code is 200:
            return response.json()['groups'][0]

        return None

    def get_groups(self, **kwargs):
        response = self.__request("GET", "groups?" + urlencode(kwargs, False))
        if response.status_code is 200:
            return response.json()['groups']

        return None

    def get_all_groups(self, **kwargs):
        return self.__paging_get("groups", **kwargs)

    def get_linked_account(self, linked_account_id):
        response = self.__request("GET", "linked_accounts/" + str(linked_account_id))
        if response.status_code is 200:
            return response.json()['linked_accounts'][0]

        return None

    def get_linked_account_providers(self):
        response = self.__request("GET", "linked_account_providers")
        if response.status_code is 200:
            return response.json()['linked_account_providers']

        return None

    def get_custom_field(self, custom_field_id):
        response = self.__request("GET", "custom_fields?id=" + str(custom_field_id))
        if response.status_code is 200:
            return response.json()['custom_fields'][0]

        return None

    def get_custom_fields(self):
        response = self.__request("GET", "custom_fields")
        if response.status_code is 200:
            return response.json()['custom_fields']

        return None

    def get_statuses(self, **kwargs):
        response = self.__request("GET", "statuses?" + urlencode(kwargs, False))
        if response.status_code is 200:
            return response.json()['statuses']

        return None

    def get_all_statuses(self, **kwargs):
        return self.__paging_get("statuses", **kwargs)
