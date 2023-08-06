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


class ActionClient(_Client):
    """
    A client for the Cortex Actions API
    """

    URIs = {'invoke': 'actions/{action_name}/invoke', 'logs': 'actions/{action_name}/logs'}

    def invoke_action(self, action_name, params: Dict[str, object]) -> Dict[str, object]:
        """
        Invoke an Action.
        :param action_name: the name of the Action to invoke
        :param params: the body params to send the Action
        :return: the result of calling the Action
        """
        uri = self.URIs['invoke'].format(action_name=action_name)
        return self._post_json(uri, params)

    def get_logs(self, action_name) -> Dict[str, object]:
        """
        Get the most recent logs for an Action
        :param action_name: the Action name to retrieve logs for
        :return: the most recent logs for the requested Action
        """
        uri = self.URIs['logs'].format(action_name=action_name)
        return self._get_json(uri)
