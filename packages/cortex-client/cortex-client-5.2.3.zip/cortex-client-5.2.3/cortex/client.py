"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import jwt
import time
from cortex_client import DatasetsClient, ModelClient, AuthenticationClient
from cortex_client.serviceconnector import ServiceConnector
from .agent import Agent
from .skill import Skill
from .dataset import Dataset
from .exceptions import AuthenticationException, TokenExpiredException
from .logger import getLogger


_DEFAULT_API_ENDPOINT = 'https://api.cortex.insights.ai'
_DEFAULT_API_VERSION = 3

_msg_token_exp_no_creds = """
Your Cortex token is expired and the required credentials for auto-refresh have not been provided.  Account, username,
and password must be supplied.  Please login again to retrieve a valid token.
"""

log = getLogger(__name__)


class _Token(object):

    def __init__(self, auth_client: AuthenticationClient, token: str, account: str, username: str, password: str):
        self._auth = auth_client
        self._token = token
        self._account = account
        self._username = username
        self._password = password

        self._jwt = None
        if token:
            self._jwt = jwt.decode(self._token, verify=False)

    def login(self):
        try:
            log.info('Login with user %s/%s' % (self._account, self._username))
            self._token = self._auth.fetch_auth_token(self._account, self._username, self._password)
        except Exception as e:
            raise AuthenticationException(str(e))

        self._jwt = jwt.decode(self._token, verify=False)

    def is_expired(self):
        current_time = time.time()
        return not self._jwt or (self._jwt.get('exp', current_time) < current_time)

    @property
    def token(self):
        # Attempt to auto-refresh expired tokens
        if self.is_expired():
            if not self._account or not self._username or not self._password:
                raise TokenExpiredException(_msg_token_exp_no_creds)
            self.login()

        return self._token


class Client(object):

    """
    API client used to access Agents, Skills, and Datasets.
    """

    def __init__(self, url: str, token: _Token, version: int = 3, verify_ssl_cert: bool = False):
        self._token = token
        self._url = url
        self._version = version
        self._verify_ssl_cert = verify_ssl_cert

    def agent(self, name: str) -> Agent:
        return Agent.get_agent(name, self._mk_connector())

    def skill(self, name: str) -> Agent:
        return Skill.get_skill(name, self._mk_connector())

    def dataset(self, name: str) -> Dataset:
        ds_client = DatasetsClient(self._url, self._version, self._token.token)
        return Dataset.get_dataset(name, ds_client)

    def _mk_connector(self):
        return ServiceConnector(self._url, self._version, self._token.token)


class Cortex(object):

    """
    Entry point to the Cortex API.
    """

    @staticmethod
    def client(api_endpoint:str=None, api_version:int=_DEFAULT_API_VERSION, verify_ssl_cert:bool=False, token:str=None, account:str=None, username:str=None, password:str=None):
        if not api_endpoint:
            api_endpoint = os.getenv('CORTEX_URI', _DEFAULT_API_ENDPOINT)

        if not token:
            token = os.getenv('CORTEX_TOKEN')

        if not account:
            account = os.getenv('CORTEX_ACCOUNT')

        if not username:
            username = os.getenv('CORTEX_USERNAME')

        if not password:
            password = os.getenv('CORTEX_PASSWORD')

        auth = AuthenticationClient(api_endpoint, version=2)
        t = _Token(auth, token, account, username, password)

        return Client(url=api_endpoint, version=api_version, token=t, verify_ssl_cert=verify_ssl_cert)
