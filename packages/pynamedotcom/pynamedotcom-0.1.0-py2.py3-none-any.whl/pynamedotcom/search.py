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
"""pynamedotcom search module."""

from __future__ import print_function
from __future__ import unicode_literals


class SearchResult(object):
    """SearchResult class."""

    def __init__(self, session, domainName, sld, tld,
                 purchasable=False, premium=False, purchasePrice=None,
                 purchaseType=None, renewalPrice=None):
        """Construct SearchResult object instance."""
        self.session = session
        self._name = domainName
        self._sld = sld
        self._tld = tld
        self._purchasable = purchasable
        self._premium = premium
        self._purchase_price = purchasePrice
        self._purchase_type = purchaseType
        self._renewal_price = renewalPrice

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def __getattr__(self, name):
        """Get private attributes."""
        try:
            return self.__getattribute__("_{}".format(name))
        except AttributeError:
            raise AttributeError("{} object has no attribute {}"
                                 .format(self.__class__, name))
