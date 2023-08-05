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
"""pynamedotcom decorators module."""

from __future__ import print_function
from __future__ import unicode_literals

import functools


def require_type(typ):
    """Decorate func to check type of 'value' argument before calling."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, value, *args, **kwargs):
            if not isinstance(value, typ):
                raise TypeError(
                    "method {} requires value argument of type {}, got {} ({})"
                    .format(func.__name__, typ, value, type(value)))
            return func(self, value, *args, **kwargs)
        return wrapper
    return decorator


def readonly(func):
    """Decorate a property setter to raise make it read-only."""
    @functools.wraps(func)
    def wrapper(self, value, *args, **kwargs):
        raise AttributeError("attribute {} is read-only".format(func.__name__))
    return wrapper
