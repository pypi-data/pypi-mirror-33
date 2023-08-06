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

from typing import Dict
from .client import _Client


class SessionClient(_Client):
    """
    A client for the Cortex Sessions API
    """

    URIs = {'start': 'sessions/start', 'get': 'sessions/{session_id}', 'put': 'sessions/{session_id}', 'delete': 'sessions/{session_id}'}

    def start_session(self, ttl=None, instance_id=None) -> str:
        """
        Start a new session.

        :param ttl: sessions will expire in 15 minutes unless the ttl is specified
        :param instance_id: an optional ID that scopes this session to a deployed Agent instance

        :return: the ID of the new Session
        """
        uri = self.URIs['start']
        params = {}
        if ttl:
            params['ttl'] = ttl
        if instance_id:
            params['instance_id'] = instance_id

        result = self._post_json(uri, params)
        return result.get('sessionId')

    def get_session_data(self, session_id, key=None) -> Dict[str, object]:
        """
        Get data for a specific Session.

        :param session_id: the ID of the Session to query
        :param key: an optional key in the Session memory.  The entire Session memory is returned if the key is not specified.

        :return: a Dict containing the requested Session data.
        """
        uri = self.URIs['get'].format(session_id=session_id)
        if key:
            uri += '?key={key}'.format(key=key)

        result = self._get_json(uri)
        return result.get('state', {})

    def put_session_data(self, session_id, data: Dict):
        """
        Add data to an existing Session.

        :param session_id: the ID of the Session to modify
        :param data: a Dict containing the new Session keys to set

        :return: None
        """
        uri = self.URIs['put'].format(session_id=session_id)
        return self._post_json(uri, data)

    def delete_session(self, session_id):
        """
        Delete a Session.

        :param session_id: the ID of the Session to delete

        :return: None
        """
        uri = self.URIs['delete'].format(session_id=session_id)
        return self._request_json(uri, method='DELETE')
