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
from .camel import Document


class Message(Document):
    """

    """

    def __init__(self, params:Dict = None):
        if params is None:
            params = {}

        super().__init__(params, False)
        self._params = params

    def to_params(self) -> Dict:
        return self._params

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if not key.startswith('_'):
            self._params[key] = value

    def as_pandas(self, client):
        if not hasattr(self, 'payload') or self.payload is None:
            raise AttributeError('Message is missing payload attribute')

        columns = []
        values = []

        ds_ref = self.payload.get('$ref')
        if ds_ref:
            ds = client.dataset(ds_ref)
            df = ds.get_dataframe()
            columns = df.get('columns')
            values = df.get('values')
        elif 'records' in self.payload:
            records = self.payload.get('records')
            if len(records) > 0:
                columns = records[0].keys()
                for obj in records:
                    values.append([obj[key] for key in columns])
        else:
            values = self.payload.get('values')
            if not values:
                raise ValueError('Invalid DataFrame: values missing from payload')

            columns = self.payload.get('columns')
            if not columns:
                raise ValueError('Invalid DataFrame: columns missing from payload')

        try:
            import pandas as pd
            return pd.DataFrame(values, columns=columns)
        except ImportError:
            # TODO warn
            return {'columns': columns, 'values': values}

    @staticmethod
    def with_payload(payload):
        return Message({'payload': payload})