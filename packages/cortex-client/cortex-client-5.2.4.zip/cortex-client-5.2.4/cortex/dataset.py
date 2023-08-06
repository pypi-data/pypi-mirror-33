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

from cortex_client import DatasetsClient
from .logger import getLogger
from .camel import CamelResource

log = getLogger(__name__)


class Dataset(CamelResource):

    """

    """

    def __init__(self, ds, client: DatasetsClient):
        super().__init__(ds)
        self._client = client

    @staticmethod
    def get_dataset(name, client: DatasetsClient):
        """
        Fetches a Dataset to work with.
        :param name: the name of the dataset to retrieve.
        :return: a Dataset object.
        """
        uri = '/'.join(['datasets', name])
        r = client._serviceconnector.request('GET', uri)
        r.raise_for_status()

        return Dataset(r.json(), client)

    def get_dataframe(self):
        return self._client.get_dataframe(self.name)

    def get_stream(self):
        return self._client.get_stream(self.name)

    def as_pandas(self):
        df = self.get_dataframe()
        columns = df.get('columns')
        values = df.get('values')

        try:
            import pandas as pd
            return pd.DataFrame(values, columns=columns)
        except ImportError:
            log.warn('Pandas is not installed, please run `pip install pandas` or equivalent in your environment')
            return {'columns': columns, 'values': values}
