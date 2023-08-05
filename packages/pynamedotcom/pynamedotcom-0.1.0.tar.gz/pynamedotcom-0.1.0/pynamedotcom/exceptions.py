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
"""pynamedotcom exceptions module."""

from __future__ import print_function
from __future__ import unicode_literals


class BaseException(Exception):
    """Base pynamedotcom exception class."""
    pass


class DomainUnlockTimeError(BaseException):
    """
    Error indicating that the specified domain cannot be unlocked until the
    specified time.
    """
    pass


class NameserverUpdateError(BaseException):
    """
    Error indicating a failure setting the delegation NS resource records on a
    domain. Usually because of missing "glue" records.
    """
    pass
