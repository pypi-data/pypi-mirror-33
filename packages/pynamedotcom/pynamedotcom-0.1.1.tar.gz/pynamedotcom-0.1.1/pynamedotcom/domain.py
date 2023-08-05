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
"""pynamedotcom Domain module."""

from __future__ import print_function
from __future__ import unicode_literals

import logging

from requests.exceptions import HTTPError

from pynamedotcom.contact import Contact
from pynamedotcom.decorators import readonly, require_type
from pynamedotcom.exceptions import (DomainUnlockTimeError,
                                     NameserverUpdateError)


class Domain(object):
    """Domain class."""

    def __init__(self, session, **kwargs):
        """Construct Domain object instance."""
        self.session = session
        self._set(**kwargs)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)

    def _set(self, domainName, nameservers=None, contacts=None,
             privacyEnabled=False, locked=False, autorenewEnabled=False,
             expireDate=None, createDate=None, renewalPrice=0):
        """Set local properties."""
        self._name = domainName
        self._nameservers = nameservers
        self._privacy = privacyEnabled
        self._locked = locked
        self._autorenew = autorenewEnabled
        self._expiry = expireDate
        self._created = createDate
        self._renewal_price = renewalPrice
        self._contacts = {}
        for role, contact in contacts.items():
            self._contacts[role] = Contact(session=self.session, **contact)

    def refresh(self):
        """Retrieve domain properties."""
        resp = self.session._get(endpoint="domains/{}".format(self.name))
        self._set(**resp.json())
        return self

    @property
    def name(self):
        return self._name

    @name.setter
    @readonly
    def name(self, value):
        pass  # pragma: no cover

    @property
    def nameservers(self):
        return self._nameservers

    @nameservers.setter
    @require_type(list)
    def nameservers(self, value):
        logging.getLogger(__name__).debug("setting {}.nameservers = {}"
                                          .format(self, value))
        endpoint = "domains/{}:setNameservers".format(self.name)
        data = {
            "nameservers": value
        }
        try:
            resp = self.session._post(endpoint=endpoint, data=data)
            self._set(**resp.json())
        except HTTPError as e:
            resp = e.response
            data = resp.json()
            if resp.status_code == 500 \
                    and "Data Management Policy Violation" in data["details"]:
                raise NameserverUpdateError(data["details"])
            else:
                raise e

    @property
    def contacts(self):
        return self._contacts

    @contacts.setter
    def contacts(self, value):
        raise NotImplementedError

    @property
    def privacy(self):
        return self._privacy

    @privacy.setter
    def privacy(self, value):
        raise NotImplementedError

    @property
    def locked(self):
        return self._locked

    @locked.setter
    @require_type(bool)
    def locked(self, value):
        logging.getLogger(__name__).debug("setting {}.locked = {}"
                                          .format(self, value))
        if value:
            endpoint = "domains/{}:lock".format(self.name)
        else:
            endpoint = "domains/{}:unlock".format(self.name)
        try:
            resp = self.session._post(endpoint=endpoint)
            self._set(**resp.json())
        except HTTPError as e:
            resp = e.response
            data = resp.json()
            if resp.status_code == 400 \
                    and "Domain can not be unlocked until" in data["details"]:
                raise DomainUnlockTimeError(data["details"])
            else:
                raise e

    @property
    def autorenew(self):
        return self._autorenew

    @autorenew.setter
    @require_type(bool)
    def autorenew(self, value):
        logging.getLogger(__name__).debug("setting {}.autorenew = {}"
                                          .format(self, value))
        if value:
            endpoint = "domains/{}:enableAutorenew".format(self.name)
        else:
            endpoint = "domains/{}:disableAutorenew".format(self.name)
        resp = self.session._post(endpoint=endpoint)
        self._set(**resp.json())

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    @readonly
    def expiry(self, value):
        pass  # pragma: no cover

    @property
    def created(self):
        return self._created

    @created.setter
    @readonly
    def created(self, value):
        pass  # pragma: no cover

    @property
    def renewal_price(self):
        return self._renewal_price

    @renewal_price.setter
    @readonly
    def renewal_price(self, value):
        pass  # pragma: no cover
