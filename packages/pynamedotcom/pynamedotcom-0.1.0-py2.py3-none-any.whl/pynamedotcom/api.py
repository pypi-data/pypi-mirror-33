# Copyright (c) 2018 Ben Maddison. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""pynamedotcom API module."""

from __future__ import print_function
from __future__ import unicode_literals

import logging
import requests
from requests.auth import HTTPBasicAuth

from pynamedotcom.domain import Domain
from pynamedotcom.search import SearchResult


class API(object):
    """API client library class."""

    def __init__(self, user=None, token=None,
                 host="api.name.com", version=4):
        """Construct API instance."""
        self.base_url = "https://{}/v{}".format(host, version)
        self.auth = HTTPBasicAuth(user, token)

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager."""
        pass

    def _get(self, endpoint=None, params=None):
        """Make a HTTP GET request."""
        url = "{}/{}".format(self.base_url, endpoint)
        resp = requests.get(url, params=params, auth=self.auth)
        logging.getLogger(__name__).debug(resp.json())
        resp.raise_for_status()
        return resp

    def _post(self, endpoint=None, data=None):
        """Make a HTTP POST request."""
        url = "{}/{}".format(self.base_url, endpoint)
        resp = requests.post(url, json=data, auth=self.auth)
        logging.getLogger(__name__).debug(resp.json())
        resp.raise_for_status()
        return resp

    def ping(self):
        """Check service reachability."""
        resp = self._get(endpoint="hello")
        return resp.json()

    def domain(self, name):
        """Get a domain."""
        resp = self._get(endpoint="domains/{}".format(name))
        return Domain(session=self, **resp.json())

    @property
    def domains(self):
        """Get list of domains as a generator."""
        resp = self._get(endpoint="domains")
        if "domains" in resp.json():
            for domain in resp.json()["domains"]:
                yield domain["domainName"]
        else:
            return

    def check_availability(self, name):
        """Check domain name availablility."""
        search_data = {
            'domainNames': [name]
        }
        resp = self._post(endpoint="domains:checkAvailability",
                          data=search_data)
        for result in resp.json()['results']:
            if result['domainName'] == name:
                return SearchResult(session=self, **result)
        return False
