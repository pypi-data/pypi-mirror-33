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
"""pynamedotcom contact module."""

from __future__ import print_function
from __future__ import unicode_literals


ROLES = ["admin", "tech", "registrant", "billing"]


class Contact(object):
    """Contact class."""

    def __init__(self, session, firstName=None, lastName=None,
                 companyName=None, address1=None, address2=None,
                 city=None, state=None, zip=None, country=None,
                 phone=None, fax=None, email=None):
        """Construct SearchResult object instance."""
        self.session = session
        self._first_name = firstName
        self._last_name = lastName
        self._company_name = companyName
        self._address = {
            "street": [address1, address2],
            "city": city,
            "state": state,
            "zip": zip,
            "country": country
        }
        self._phone = phone
        self._fax = fax
        self._email = email

    def __repr__(self):
        if self.company_name:
            return "{} {} ({}) <{}>".format(self.first_name, self.last_name,
                                            self.company_name, self.email)
        else:
            return "{} {} <{}>".format(self.first_name, self.last_name,
                                       self.email)

    def __getattr__(self, name):
        """Get private attributes."""
        try:
            return self.__getattribute__("_{}".format(name))
        except AttributeError:
            raise AttributeError("{} object has no attribute {}"
                                 .format(self.__class__, name))
